import csv
import datetime
import io
import json
import logging
import pendulum
import zipfile
from bs4 import BeautifulSoup
from google.transit import gtfs_realtime_pb2 as gtfs_realtime
from gtfs_realtime_translators.factories import Alert, FeedMessage

logger = logging.getLogger(__name__)

class DeVVSAlertGtfsRealtimeTranslator:
    ''' 
    Fixes VVS GTFS-RT-Alert feed (available via https://gtfsr-servicealerts.vvs.de) by:
    * converting route_ids to their current form in the static GTFS feed
    * explodes parent stop ids, which are not explicitly provided in GTFS (TODO: filter based on route_id/direction_id)
    * guesses cause and effect from partial string matching of headers and description
    * converting the alert description from it's html encoded from into plain text
    * TODO: sets severity_level (need to figure out appropriate levels)

    Note: in case a stop_id or route_id could not be matched, a warning is logged. If 
    an effect or cause could not be extracted, an info message. Please monitor the logs of
    this translator to be aware of any failing translation logic and adapt the code...
    '''

    TIMEZONE = 'Europe/Berlin'

    def __init__(self, gtfsfile, high_prio_keywords = [], high_prio_route_ids = []):
        self.id_mapper = DeVVSGtfsIdMapper(gtfsfile)
        self.high_prio_keywords = high_prio_keywords
        self.high_prio_route_ids = high_prio_route_ids

    def __call__(self, data):
        feed = gtfs_realtime.FeedMessage()
        feed.ParseFromString(data)
        entities = [self.__map_alert(idx, feedEntity) for idx, feedEntity in enumerate(feed.entity)]
        message = FeedMessage.create(entities=entities)
        message.header.incrementality = feed.header.incrementality
        message.header.timestamp = feed.header.timestamp
        return message

    def __map_alert(self, _id, entity):
        informed_entity = self.__map_informed_entities(entity.alert.informed_entity)
        feedEntity = Alert.create_from(entity, informed_entity = informed_entity)

        
        header = entity.alert.header_text.translation[0].text.lower() if entity.alert.HasField('header_text') else ''
        if entity.alert.HasField('description_text'):
            html_encoded_description = entity.alert.description_text.translation[0].text
            soup = BeautifulSoup(html_encoded_description, "lxml")
            description = soup.get_text()
            feedEntity.alert.description_text.translation[0].text = description
        else:
            description = ''

        if not feedEntity.alert.HasField('effect') or feedEntity.alert.effect == gtfs_realtime.Alert.Effect.UNKNOWN_EFFECT:
            feedEntity.alert.effect = self.__map_effect(header, description.lower())

        if not feedEntity.alert.HasField('cause') or feedEntity.alert.cause == gtfs_realtime.Alert.Cause.UNKNOWN_CAUSE:
            feedEntity.alert.cause = self.__map_cause(header, description.lower())
        
        self.__set_severity_level(feedEntity)
        # TODO other attributes
        return feedEntity

    def __map_effect(self, header, description) -> int:
        """
        NO_SERVICE = 1;
        REDUCED_SERVICE = 2;
        SIGNIFICANT_DELAYS = 3;
        DETOUR = 4;
        ADDITIONAL_SERVICE = 5;
        MODIFIED_SERVICE = 6;
        OTHER_EFFECT = 7;
        UNKNOWN_EFFECT = 8;
        STOP_MOVED = 9;
        NO_EFFECT = 10;
        ACCESSIBILITY_ISSUE = 11;
        """
        
        if any(map(header.__contains__, ['verleg', 'bahnen halten'])) or any(map(description.__contains__, ['ersatzhalt'])):
            return gtfs_realtime.Alert.Effect.STOP_MOVED
        if 'nicht angefahren' in header or 'entfall' in header or 'entfällt' in header or 'gesperrt' in header or 'ausfall' in header:
            return gtfs_realtime.Alert.Effect.NO_SERVICE
        if 'kein barrierefrei' in header or ('aufzug' in header and 'betrieb' in header):
            return gtfs_realtime.Alert.Effect.ACCESSIBILITY_ISSUE
        if any(map(header.__contains__, ['fahrplanänderung', 'umleitung', 'verlängerung'])):
            return gtfs_realtime.Alert.Effect.MODIFIED_SERVICE # or reduced?
        if any(map(header.__contains__, ['sportveranstaltung', 'konzert', 'neue haltestelle'])):
            return gtfs_realtime.Alert.Effect.ADDITIONAL_SERVICE # wild guessing, all cases I've seen add additional trips
        if 'regulär' in header:
            return gtfs_realtime.Alert.Effect.NO_EFFECT # wild guessing, all cases I've seen announce restore of regular service
    
        logger.info(f'Unknown effect for: {header}')
        return gtfs_realtime.Alert.Effect.UNKNOWN_EFFECT

    def __map_cause(self, header, description) -> int:
        """
        UNKNOWN_CAUSE = 1;
        OTHER_CAUSE = 2;        // Not machine-representable.
        TECHNICAL_PROBLEM = 3;
        STRIKE = 4;             // Public transit agency employees stopped working.
        DEMONSTRATION = 5;      // People are blocking the streets.
        ACCIDENT = 6;
        HOLIDAY = 7;
        WEATHER = 8;
        MAINTENANCE = 9;
        CONSTRUCTION = 10;
        POLICE_ACTIVITY = 11;
        MEDICAL_EMERGENCY = 12;
        """

        if self.__header_or_desc_contains_any(header, description, ['bauarbeiten', 'baustelle']):
            return gtfs_realtime.Alert.Cause.CONSTRUCTION
        if self.__header_or_desc_contains_any(header, description, ['konzert', 'veranstaltung']):
            return gtfs_realtime.Alert.Cause.OTHER_CAUSE # IMHO a cause EVENT would make sense
        if self.__header_or_desc_contains_any(header, description, ['erdrutsch', 'hangrutsch', 'unwetter']):
            return gtfs_realtime.Alert.Cause.WEATHER # maybe one day, there'll be a Cause NATURAL_DISASTER
        if self.__header_or_desc_contains_any(header, description, ['unfall']):
            return gtfs_realtime.Alert.Cause.ACCIDENT

        logger.info(f'Unknown cause for: {header}')
        return gtfs_realtime.Alert.Cause.UNKNOWN_CAUSE
     
    @staticmethod
    def __header_or_desc_contains_any(header, desc, substring_list):
        return any(map(header.__contains__, substring_list)) or any(map(desc.__contains__, substring_list))

    def __map_informed_entities(self, informed_entities):
        mapped_entities = []
        for entity in informed_entities:
            new_entity = {}
            if entity.HasField('agency_id'):
                new_entity['agency_id'] = entity.agency_id
            if entity.HasField('route_id'):
                new_entity['route_id'] = self.id_mapper.map_route_id(entity.route_id)
            if entity.HasField('direction_id'):
                new_entity['direction_id'] = entity.direction_id
            # in case other selectors need to be added, add them here, before stops are exploded

            # as a last step, explode multiple stop ids if only parent stop is referenced
            if entity.HasField('stop_id'):
                # TODO: if we'd know which route_id/direction_ids are served at this stop, we'd could filter
                # non-served out, but for now, we let consumers do such filtering
                for stop_id in self.id_mapper.map_stop_id(entity.stop_id):
                    per_stop_entity = dict(new_entity)
                    per_stop_entity['stop_id'] = stop_id
                    mapped_entities.append(per_stop_entity)
            else:
                mapped_entities.append(new_entity)
                 
        return mapped_entities

    def __set_severity_level(self, entity):
        # set default severity
        entity.alert.severity_level = 3
        if self.__starts_latest_in(entity, datetime.timedelta(weeks=1)):
            # if one of keywords is contained in message, set prio to 1
            if entity.alert.HasField('description_text'):#
                description = entity.alert.description_text.translation[0].text
                for high_prio_keyword in self.high_prio_keywords:      
                    if high_prio_keyword in description:
                        logger.debug(f'Set severity for: {description}')
                        entity.alert.severity_level = 4
            # if at least one of informed entity route_ids is contained in this set, set prio to 1
            for informed_entity in entity.alert.informed_entity:
                if informed_entity.HasField('route_id') and informed_entity.route_id in self.high_prio_route_ids:
                    logger.debug(f'Set severity for: {informed_entity.route_id}')
                    entity.alert.severity_level = 4

    def __now(self):
        return datetime.datetime.now()

    def __starts_latest_in(self, entity, timedelta):
        now = self.__now()
        latest_start_seconds = (now + timedelta).timestamp()
        for period in entity.alert.active_period:
            if period.HasField('start') and period.start <= latest_start_seconds:
                return True
        return False

class DeVVSGtfsIdMapper:

    def __init__(self, gtfsfile):
        self._load_stops(gtfsfile)
        self._load_routes(gtfsfile)

    def _for_each_row_in_gtfs_file(self, gtfsfile, feature_file, handle_row):
        zf = zipfile.ZipFile(gtfsfile)
        parent_stations_stops = {}
        with zf.open(feature_file, 'r') as csvfile:
            csvreader = csv.DictReader(io.TextIOWrapper(csvfile, 'utf-8-sig'), delimiter=',', quotechar='"')
            for row in csvreader:
                handle_row(row)

    def _parent_station(self, stop):
        parent_station = stop.get('parent_station')
        if parent_station is None or parent_station == '':
            pos = self.find_nth(stop['stop_id'], ':', 3)
            if pos > 0:
                parent_station = stop['stop_id'][:pos]
        
        return parent_station
        
    def _load_stops(self, gtfsfile):
        parent_stations_stops = {}
        def handle_stop(stop):
            if stop['location_type'] is not None and stop['location_type'] not in ['', '0']:
                return
            parent_station = self._parent_station(stop)
            if parent_station not in parent_stations_stops:
                parent_stations_stops[parent_station] = set()
            parent_stations_stops[parent_station].add(stop['stop_id'])

        self._for_each_row_in_gtfs_file(gtfsfile, 'stops.txt', handle_stop)
        self.parent_stations_stops = parent_stations_stops

    def _load_routes(self, gtfsfile):
        route_ids = set()
        def handle_route(route):
            route_ids.add(route['route_id'])

        self._for_each_row_in_gtfs_file(gtfsfile, 'routes.txt', handle_route)
        self.route_ids = route_ids

    @staticmethod
    def find_nth(wholestring: str, pattern: str, n: int) -> int:
        start = wholestring.find(pattern)
        while start >= 0 and n > 1:
            start = wholestring.find(pattern, start+len(pattern))
            n -= 1
        return start

    def map_route_id(self, gtfsrt_route_id: str):
        if gtfsrt_route_id in self.route_ids:
            return gtfsrt_route_id

        if gtfsrt_route_id.startswith('de:vvs:vvs'):
            route_id_components = gtfsrt_route_id[len("de:vvs:vvs-"):].split("-")
            route_type = route_id_components[0]
            route_name_components= route_id_components[1].split(':')
            route_name = route_name_components[0].zfill(3)
            suffix = route_name_components[1] if len(route_name_components[1]) > 0 else '_'
            if route_type == '11' and route_name not in ['011', '064', '074a']:
                # All but the following route_types 11 are in de:vvs:vvs-11-xxx: form
                #"de:vvs:11011_:","VVS","RB11","Kornwestheim - Untertürkheim","2","8f908f","FFFFFF","VVS_ticketing"
                #"de:vvs:11064_:","VVS","RB64","Oberlenningen - Kirchheim (T)","2","8f908f","FFFFFF","VVS_ticketing"
                #"de:vvs:11074s:","VVS","S8","(Herrenberg -) Eutingen i. G. - Freudenstadt","2","8f908f","FFFFFF","VVS_ticketing"
                return gtfsrt_route_id
            if route_type in ['76','77','81']:
                # All of the above route_types are in de:vvs:vvs-yy-xxx: form => do not transform
                mapped_route_id = gtfsrt_route_id

            else:
                mapped_route_id = f'de:vvs:{route_type}{route_name}{suffix}:'
        elif gtfsrt_route_id.startswith('vvs:'):
            route_id_components = gtfsrt_route_id[len("vvs:"):].split(":")
            route_type = route_id_components[0][0:2]
            route_name = route_id_components[0][2:].zfill(3)
            suffix = route_id_components[1] if route_id_components[1] != ' ' else '_'
            if route_type == '11' and route_name not in ['011', '064', '074a']:
                # All but the following route_types 11 are in de:vvs:vvs-11-xxx: form
                #"de:vvs:11011_:","VVS","RB11","Kornwestheim - Untertürkheim","2","8f908f","FFFFFF","VVS_ticketing"
                #"de:vvs:11064_:","VVS","RB64","Oberlenningen - Kirchheim (T)","2","8f908f","FFFFFF","VVS_ticketing"
                #"de:vvs:11074s:","VVS","S8","(Herrenberg -) Eutingen i. G. - Freudenstadt","2","8f908f","FFFFFF","VVS_ticketing"
                return gtfsrt_route_id
            if route_type in ['76','77','81']:
                # All of the above route_types are in de:vvs:vvs-yy-xxx: form => do not transform
                mapped_route_id = gtfsrt_route_id

            else:
                mapped_route_id = f'de:vvs:{route_type}{route_name}{suffix}:'
        else:
            mapped_route_id = gtfsrt_route_id

        special_cases = {
            'de:vvs:30014e:': 'de:vvs:300014e:'
        }
        if mapped_route_id in special_cases:
            mapped_route_id = special_cases[mapped_route_id]

        if mapped_route_id not in self.route_ids:
            logger.warning(f'Warning: neither original gtfsrt route_id {gtfsrt_route_id} nor mapped route_id {mapped_route_id} in static GTFS feed')

        return mapped_route_id

    def map_stop_id(self, gtfsrt_stop_id: str):
    
        if gtfsrt_stop_id not in self.parent_stations_stops:
            logger.warning(f'Warning: stop_id {gtfsrt_stop_id} not in static GTFS feed')
            return { gtfsrt_stop_id }

        return self.parent_stations_stops[gtfsrt_stop_id]           
