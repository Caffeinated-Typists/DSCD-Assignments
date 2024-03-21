# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: raft.proto
# Protobuf Python Version: 4.25.1
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nraft.proto\"-\n\tDbRequest\x12\x0c\n\x04type\x18\x01 \x01(\x05\x12\x12\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x04.Log\"0\n\nDbResponse\x12\x0e\n\x06status\x18\x01 \x01(\x05\x12\x12\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32\x04.Log\"\x93\x01\n\x14\x41ppendEntriesRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x11\n\tleader_id\x18\x02 \x01(\x05\x12\x14\n\x0cprev_log_idx\x18\x03 \x01(\x05\x12\x15\n\rprev_log_term\x18\x04 \x01(\x05\x12\x19\n\x11leader_commit_idx\x18\x05 \x01(\x05\x12\x12\n\x04\x64\x61ta\x18\x06 \x03(\x0b\x32\x04.Log\"6\n\x15\x41ppendEntriesResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x0f\n\x07success\x18\x02 \x01(\x08\"\x9a\x01\n\x16InstallSnapshotRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x11\n\tleader_id\x18\x02 \x01(\x05\x12\x15\n\rlast_incl_idx\x18\x03 \x01(\x05\x12\x16\n\x0elast_incl_term\x18\x04 \x01(\x05\x12\x0e\n\x06offset\x18\x05 \x01(\x05\x12\x12\n\x04\x64\x61ta\x18\x06 \x03(\x0b\x32\x04.Log\x12\x0c\n\x04\x64one\x18\x07 \x01(\x08\"\'\n\x17InstallSnapshotResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\"W\n\x03Log\x12\x18\n\x03\x63md\x18\x01 \x01(\x0e\x32\x0b.Log.action\x12\x0b\n\x03key\x18\x02 \x01(\t\x12\r\n\x05value\x18\x03 \x01(\t\"\x1a\n\x06\x61\x63tion\x12\x07\n\x03GET\x10\x00\x12\x07\n\x03SET\x10\x01\"^\n\x0bVoteRequest\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x14\n\x0c\x63\x61ndidate_id\x18\x02 \x01(\x05\x12\x14\n\x0clast_log_idx\x18\x03 \x01(\x05\x12\x15\n\rlast_log_term\x18\x04 \x01(\x05\"2\n\x0cVoteResponse\x12\x0c\n\x04term\x18\x01 \x01(\x05\x12\x14\n\x0cvote_granted\x18\x02 \x01(\x08\x32\xbe\x01\n\x04Raft\x12@\n\rAppendEntries\x12\x15.AppendEntriesRequest\x1a\x16.AppendEntriesResponse\"\x00\x12,\n\x0bRequestVote\x12\x0c.VoteRequest\x1a\r.VoteResponse\"\x00\x12\x46\n\x0fInstallSnapshot\x12\x17.InstallSnapshotRequest\x1a\x18.InstallSnapshotResponse\"\x00\x32\x34\n\x08\x44\x61tabase\x12(\n\x0bRequestData\x12\n.DbRequest\x1a\x0b.DbResponse\"\x00\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'raft_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_DBREQUEST']._serialized_start=14
  _globals['_DBREQUEST']._serialized_end=59
  _globals['_DBRESPONSE']._serialized_start=61
  _globals['_DBRESPONSE']._serialized_end=109
  _globals['_APPENDENTRIESREQUEST']._serialized_start=112
  _globals['_APPENDENTRIESREQUEST']._serialized_end=259
  _globals['_APPENDENTRIESRESPONSE']._serialized_start=261
  _globals['_APPENDENTRIESRESPONSE']._serialized_end=315
  _globals['_INSTALLSNAPSHOTREQUEST']._serialized_start=318
  _globals['_INSTALLSNAPSHOTREQUEST']._serialized_end=472
  _globals['_INSTALLSNAPSHOTRESPONSE']._serialized_start=474
  _globals['_INSTALLSNAPSHOTRESPONSE']._serialized_end=513
  _globals['_LOG']._serialized_start=515
  _globals['_LOG']._serialized_end=602
  _globals['_LOG_ACTION']._serialized_start=576
  _globals['_LOG_ACTION']._serialized_end=602
  _globals['_VOTEREQUEST']._serialized_start=604
  _globals['_VOTEREQUEST']._serialized_end=698
  _globals['_VOTERESPONSE']._serialized_start=700
  _globals['_VOTERESPONSE']._serialized_end=750
  _globals['_RAFT']._serialized_start=753
  _globals['_RAFT']._serialized_end=943
  _globals['_DATABASE']._serialized_start=945
  _globals['_DATABASE']._serialized_end=997
# @@protoc_insertion_point(module_scope)
