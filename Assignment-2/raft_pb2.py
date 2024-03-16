# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
# Protobuf Python Version: 4.25.0
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\"(\n\x08Response\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x0c\n\x04info\x18\x02 \x01(\t\"-\n\tDbRequest\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x12\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x04.Log\"0\n\nDbResponse\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x12\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x04.Log\"\x93\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x11\n\tleader_id\x18\x02 \x01(\x05\x12\x14\n\x0cprev_log_idx\x18\x03 \x01(\x05\x12\x15\n\rprev_log_term\x18\x04 \x01(\x05\x12\x19\n\x11leader_commit_idx\x18\x05 \x01(\x05\x12\x12\n\x04\x64\x61ta\x18\x06 \x01(\x0b\x32\x04.Log\"6\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07success\x18\x02 \x01(\x08\"-\n\tHeartbeat\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x12\n\nlease_time\x18\x02 \x01(\x05\"\x93\x01\n\x0fInstallSnapshot\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x11\n\tleader_id\x18\x02 \x01(\x05\x12\x15\n\rlast_incl_idx\x18\x03 \x01(\x05\x12\x16\n\x0elast_incl_term\x18\x04 \x01(\x05\x12\x0e\n\x06offset\x18\x05 \x01(\x05\x12\x12\n\x04\x64\x61ta\x18\x06 \x03(\x0b\x32\x04.Log\x12\x0c\n\x04\x64one\x18\x07 \x01(\x08\"!\n\x03Log\x12\x0b\n\x03key\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\x05\"^\n\x0bVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x14\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\x05\x12\x14\n\x0clast_log_idx\x18\x03 \x01(\x05\x12\x15\n\rlast_log_term\x18\x04 \x01(\x05\"2\n\x0cVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x14\n\x0cvote_granted\x18\x02 \x01(\x08\x32\xa0\x01\n\x04Raft\x12(\n\rSendHeartbeat\x12\n.Heartbeat\x1a\t.Response\"\x00\x12@\n\rAppendEntries\x12\x15.AppendEntriesRequest\x1a\x16.AppendEntriesResponse\"\x00\x12,\n\x0bRequestVote\x12\x0c.VoteRequest\x1a\r.VoteResponse\"\x00\x32\x34\n\x08\x44\x61tabase\x12(\n\x0bRequestData\x12\n.DbRequest\x1a\x0b.DbResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_RESPONSE']._serialized_start=14
  _globals['_RESPONSE']._serialized_end=54
  _globals['_DBREQUEST']._serialized_start=56
  _globals['_DBREQUEST']._serialized_end=101
  _globals['_DBRESPONSE']._serialized_start=103
  _globals['_DBRESPONSE']._serialized_end=151
  _globals['_APPENDENTRIESREQUEST']._serialized_start=154
  _globals['_APPENDENTRIESREQUEST']._serialized_end=301
  _globals['_APPENDENTRIESRESPONSE']._serialized_start=303
  _globals['_APPENDENTRIESRESPONSE']._serialized_end=357
  _globals['_HEARTBEAT']._serialized_start=359
  _globals['_HEARTBEAT']._serialized_end=404
  _globals['_INSTALLSNAPSHOT']._serialized_start=407
  _globals['_INSTALLSNAPSHOT']._serialized_end=554
  _globals['_LOG']._serialized_start=556
  _globals['_LOG']._serialized_end=589
  _globals['_VOTEREQUEST']._serialized_start=591
  _globals['_VOTEREQUEST']._serialized_end=685
  _globals['_VOTERESPONSE']._serialized_start=687
  _globals['_VOTERESPONSE']._serialized_end=737
  _globals['_RAFT']._serialized_start=740
  _globals['_RAFT']._serialized_end=900
  _globals['_DATABASE']._serialized_start=902
  _globals['_DATABASE']._serialized_end=954
# @@protoc_insertion_point(module_scope)
