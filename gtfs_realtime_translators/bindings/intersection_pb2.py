# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: intersection.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.transit import gtfs_realtime_pb2 as gtfs__realtime__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='intersection.proto',
  package='',
  syntax='proto2',
  serialized_options=None,
  serialized_pb=_b('\n\x12intersection.proto\x1a\x13gtfs-realtime.proto\"*\n\x16IntersectionTripUpdate\x12\x10\n\x08headsign\x18\x01 \x01(\t\"\xbb\x01\n\x1aIntersectionStopTimeUpdate\x12\r\n\x05track\x18\x01 \x01(\t\x12\x45\n\x11scheduled_arrival\x18\x02 \x01(\x0b\x32*.transit_realtime.TripUpdate.StopTimeEvent\x12G\n\x13scheduled_departure\x18\x03 \x01(\x0b\x32*.transit_realtime.TripUpdate.StopTimeEvent:X\n\x18intersection_trip_update\x12\x1c.transit_realtime.TripUpdate\x18\xc3\x0f \x01(\x0b\x32\x17.IntersectionTripUpdate:p\n\x1dintersection_stop_time_update\x12+.transit_realtime.TripUpdate.StopTimeUpdate\x18\xc3\x0f \x01(\x0b\x32\x1b.IntersectionStopTimeUpdate')
  ,
  dependencies=[gtfs__realtime__pb2.DESCRIPTOR,])


INTERSECTION_TRIP_UPDATE_FIELD_NUMBER = 1987
intersection_trip_update = _descriptor.FieldDescriptor(
  name='intersection_trip_update', full_name='intersection_trip_update', index=0,
  number=1987, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)
INTERSECTION_STOP_TIME_UPDATE_FIELD_NUMBER = 1987
intersection_stop_time_update = _descriptor.FieldDescriptor(
  name='intersection_stop_time_update', full_name='intersection_stop_time_update', index=1,
  number=1987, type=11, cpp_type=10, label=1,
  has_default_value=False, default_value=None,
  message_type=None, enum_type=None, containing_type=None,
  is_extension=True, extension_scope=None,
  serialized_options=None, file=DESCRIPTOR)


_INTERSECTIONTRIPUPDATE = _descriptor.Descriptor(
  name='IntersectionTripUpdate',
  full_name='IntersectionTripUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='headsign', full_name='IntersectionTripUpdate.headsign', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=43,
  serialized_end=85,
)


_INTERSECTIONSTOPTIMEUPDATE = _descriptor.Descriptor(
  name='IntersectionStopTimeUpdate',
  full_name='IntersectionStopTimeUpdate',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='track', full_name='IntersectionStopTimeUpdate.track', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='scheduled_arrival', full_name='IntersectionStopTimeUpdate.scheduled_arrival', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='scheduled_departure', full_name='IntersectionStopTimeUpdate.scheduled_departure', index=2,
      number=3, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto2',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=88,
  serialized_end=275,
)

_INTERSECTIONSTOPTIMEUPDATE.fields_by_name['scheduled_arrival'].message_type = gtfs__realtime__pb2._TRIPUPDATE_STOPTIMEEVENT
_INTERSECTIONSTOPTIMEUPDATE.fields_by_name['scheduled_departure'].message_type = gtfs__realtime__pb2._TRIPUPDATE_STOPTIMEEVENT
DESCRIPTOR.message_types_by_name['IntersectionTripUpdate'] = _INTERSECTIONTRIPUPDATE
DESCRIPTOR.message_types_by_name['IntersectionStopTimeUpdate'] = _INTERSECTIONSTOPTIMEUPDATE
DESCRIPTOR.extensions_by_name['intersection_trip_update'] = intersection_trip_update
DESCRIPTOR.extensions_by_name['intersection_stop_time_update'] = intersection_stop_time_update
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

IntersectionTripUpdate = _reflection.GeneratedProtocolMessageType('IntersectionTripUpdate', (_message.Message,), dict(
  DESCRIPTOR = _INTERSECTIONTRIPUPDATE,
  __module__ = 'intersection_pb2'
  # @@protoc_insertion_point(class_scope:IntersectionTripUpdate)
  ))
_sym_db.RegisterMessage(IntersectionTripUpdate)

IntersectionStopTimeUpdate = _reflection.GeneratedProtocolMessageType('IntersectionStopTimeUpdate', (_message.Message,), dict(
  DESCRIPTOR = _INTERSECTIONSTOPTIMEUPDATE,
  __module__ = 'intersection_pb2'
  # @@protoc_insertion_point(class_scope:IntersectionStopTimeUpdate)
  ))
_sym_db.RegisterMessage(IntersectionStopTimeUpdate)

intersection_trip_update.message_type = _INTERSECTIONTRIPUPDATE
gtfs__realtime__pb2.TripUpdate.RegisterExtension(intersection_trip_update)
intersection_stop_time_update.message_type = _INTERSECTIONSTOPTIMEUPDATE
gtfs__realtime__pb2.TripUpdate.StopTimeUpdate.RegisterExtension(intersection_stop_time_update)

# @@protoc_insertion_point(module_scope)