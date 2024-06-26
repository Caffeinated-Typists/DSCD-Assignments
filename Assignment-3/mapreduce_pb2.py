# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: mapreduce.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fmapreduce.proto\"\x1a\n\x08Response\x12\x0e\n\x06status\x18\x01 \x01(\x08\")\n\x0b\x44oneRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0e\n\x06status\x18\x02 \x01(\x08\"F\n\nMapRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\r\n\x05start\x18\x02 \x01(\x05\x12\x0b\n\x03\x65nd\x18\x03 \x01(\x05\x12\x10\n\x08reducers\x18\x04 \x01(\x05\"\x1f\n\x10PartitionRequest\x12\x0b\n\x03idx\x18\x01 \x01(\x05\"!\n\x11PartitionResponse\x12\x0c\n\x04\x64\x61ta\x18\x01 \x01(\x0c\"C\n\rReduceRequest\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x15\n\rpartition_idx\x18\x02 \x01(\x05\x12\x0f\n\x07mappers\x18\x03 \x01(\x05\"\x1d\n\x0f\x43\x65ntroidRequest\x12\n\n\x02id\x18\x01 \x01(\x05\".\n\x0e\x43\x65ntroidResult\x12\x0e\n\x06status\x18\x01 \x01(\x08\x12\x0c\n\x04\x64\x61ta\x18\x02 \x01(\x0c\"\x07\n\x05\x45mpty2W\n\x06Master\x12$\n\x07MapDone\x12\x0c.DoneRequest\x1a\t.Response\"\x00\x12\'\n\nReduceDone\x12\x0c.DoneRequest\x1a\t.Response\"\x00\x32\x7f\n\x06Mapper\x12\x1f\n\x03Map\x12\x0b.MapRequest\x1a\t.Response\"\x00\x12\x37\n\x0cGetPartition\x12\x11.PartitionRequest\x1a\x12.PartitionResponse\"\x00\x12\x1b\n\x04Ping\x12\x06.Empty\x1a\t.Response\"\x00\x32w\n\x07Reducer\x12%\n\x06Reduce\x12\x0e.ReduceRequest\x1a\t.Response\"\x00\x12(\n\x0bGetCentroid\x12\x06.Empty\x1a\x0f.CentroidResult\"\x00\x12\x1b\n\x04Ping\x12\x06.Empty\x1a\t.Response\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'mapreduce_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_RESPONSE']._serialized_start=19
  _globals['_RESPONSE']._serialized_end=45
  _globals['_DONEREQUEST']._serialized_start=47
  _globals['_DONEREQUEST']._serialized_end=88
  _globals['_MAPREQUEST']._serialized_start=90
  _globals['_MAPREQUEST']._serialized_end=160
  _globals['_PARTITIONREQUEST']._serialized_start=162
  _globals['_PARTITIONREQUEST']._serialized_end=193
  _globals['_PARTITIONRESPONSE']._serialized_start=195
  _globals['_PARTITIONRESPONSE']._serialized_end=228
  _globals['_REDUCEREQUEST']._serialized_start=230
  _globals['_REDUCEREQUEST']._serialized_end=297
  _globals['_CENTROIDREQUEST']._serialized_start=299
  _globals['_CENTROIDREQUEST']._serialized_end=328
  _globals['_CENTROIDRESULT']._serialized_start=330
  _globals['_CENTROIDRESULT']._serialized_end=376
  _globals['_EMPTY']._serialized_start=378
  _globals['_EMPTY']._serialized_end=385
  _globals['_MASTER']._serialized_start=387
  _globals['_MASTER']._serialized_end=474
  _globals['_MAPPER']._serialized_start=476
  _globals['_MAPPER']._serialized_end=603
  _globals['_REDUCER']._serialized_start=605
  _globals['_REDUCER']._serialized_end=724
# @@protoc_insertion_point(module_scope)
