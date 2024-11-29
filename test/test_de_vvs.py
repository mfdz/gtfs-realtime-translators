import pytest
import pendulum

from gtfs_realtime_translators.translators.de_vvs import DeVVSAlertGtfsRealtimeTranslator, DeVVSGtfsIdMapper
from gtfs_realtime_translators.bindings import intersection_pb2 as intersection_gtfs_realtime
from gtfs_realtime_translators.factories import FeedMessage


@pytest.fixture
def de_vvs_alerts():
    with open('test/fixtures/de_vvs_gtfsr-alerts_20240317001430.pb', 'rb') as f:
        raw = f.read()
    return raw


def test_de_vvs_alerts(de_vvs_alerts):
    translator = DeVVSAlertGtfsRealtimeTranslator('test/fixtures/de_vvs.gtfs.zip')
    with pendulum.travel_to(pendulum.datetime(2024, 3, 17, 00, 14, 35)):
        message = translator(de_vvs_alerts)

def test_de_vvs_route_id_mapping():
    mapper = DeVVSGtfsIdMapper('test/fixtures/de_vvs.gtfs.zip')
    assert 'de:vvs:31263_:' == mapper.map_route_id('de:vvs:vvs-31-263:')
    assert 'de:vvs:34048_:' == mapper.map_route_id('de:vvs:vvs-34-48:')
    assert 'de:vvs:31901a:' == mapper.map_route_id('de:vvs:vvs-31-901:a')
    assert 'de:vvs:31X16_:' == mapper.map_route_id('vvs:31X16: :R:j24')
    assert 'de:vvs:31757u:' == mapper.map_route_id('vvs:31757:u:H:j24')
    # Special cases due to typos in routes.txt
    assert 'de:vvs:300014e:' == mapper.map_route_id('vvs:30014:e:H:j24')

def test_de_vvs_stop_id_mapping_returns_implicit_parent_stop_id():
    mapper = DeVVSGtfsIdMapper('test/fixtures/de_vvs.gtfs.zip')

    # stops.txt has these stops, which have their parent stop de:08111:109 not explicitly stated:
    #"de:08111:109:0:3","Zuffenhausen Friedhof","48.8358995841783","9.18146663215316","",""
    #"de:08111:109:0:4","Zuffenhausen Friedhof","48.8358995841783","9.18146663215316","",""
    # map_stop_id should nevertheless return these for their implicitly known parent stop id
    assert {'de:08111:109:0:3', 'de:08111:109:0:4'} == mapper.map_stop_id('de:08111:109')
