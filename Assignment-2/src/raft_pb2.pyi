from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataRequest(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: Log
    def __init__(self, data: _Optional[_Union[Log, _Mapping]] = ...) -> None: ...

class DataResponse(_message.Message):
    __slots__ = ("status", "leader_id", "data")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    status: bool
    leader_id: int
    data: Log
    def __init__(self, status: bool = ..., leader_id: _Optional[int] = ..., data: _Optional[_Union[Log, _Mapping]] = ...) -> None: ...

class AppendEntriesRequest(_message.Message):
    __slots__ = ("term", "leader_id", "prev_log_idx", "prev_log_term", "leader_commit_idx", "leader_lease", "entries")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_IDX_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    LEADER_COMMIT_IDX_FIELD_NUMBER: _ClassVar[int]
    LEADER_LEASE_FIELD_NUMBER: _ClassVar[int]
    ENTRIES_FIELD_NUMBER: _ClassVar[int]
    term: int
    leader_id: int
    prev_log_idx: int
    prev_log_term: int
    leader_commit_idx: int
    leader_lease: Lease
    entries: _containers.RepeatedCompositeFieldContainer[Log]
    def __init__(self, term: _Optional[int] = ..., leader_id: _Optional[int] = ..., prev_log_idx: _Optional[int] = ..., prev_log_term: _Optional[int] = ..., leader_commit_idx: _Optional[int] = ..., leader_lease: _Optional[_Union[Lease, _Mapping]] = ..., entries: _Optional[_Iterable[_Union[Log, _Mapping]]] = ...) -> None: ...

class AppendEntriesResponse(_message.Message):
    __slots__ = ("term", "success")
    TERM_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    term: int
    success: bool
    def __init__(self, term: _Optional[int] = ..., success: bool = ...) -> None: ...

class InstallSnapshotRequest(_message.Message):
    __slots__ = ("term", "leader_id", "last_incl_idx", "last_incl_term", "offset", "data", "done")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_INCL_IDX_FIELD_NUMBER: _ClassVar[int]
    LAST_INCL_TERM_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    DONE_FIELD_NUMBER: _ClassVar[int]
    term: int
    leader_id: int
    last_incl_idx: int
    last_incl_term: int
    offset: int
    data: _containers.RepeatedCompositeFieldContainer[Log]
    done: bool
    def __init__(self, term: _Optional[int] = ..., leader_id: _Optional[int] = ..., last_incl_idx: _Optional[int] = ..., last_incl_term: _Optional[int] = ..., offset: _Optional[int] = ..., data: _Optional[_Iterable[_Union[Log, _Mapping]]] = ..., done: bool = ...) -> None: ...

class InstallSnapshotResponse(_message.Message):
    __slots__ = ("term",)
    TERM_FIELD_NUMBER: _ClassVar[int]
    term: int
    def __init__(self, term: _Optional[int] = ...) -> None: ...

class Log(_message.Message):
    __slots__ = ("cmd", "key", "value", "term")
    class action(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NONE: _ClassVar[Log.action]
        NOOP: _ClassVar[Log.action]
        SET: _ClassVar[Log.action]
        GET: _ClassVar[Log.action]
    NONE: Log.action
    NOOP: Log.action
    SET: Log.action
    GET: Log.action
    CMD_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    TERM_FIELD_NUMBER: _ClassVar[int]
    cmd: Log.action
    key: str
    value: str
    term: int
    def __init__(self, cmd: _Optional[_Union[Log.action, str]] = ..., key: _Optional[str] = ..., value: _Optional[str] = ..., term: _Optional[int] = ...) -> None: ...

class Lease(_message.Message):
    __slots__ = ("leader_id", "time")
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    TIME_FIELD_NUMBER: _ClassVar[int]
    leader_id: int
    time: float
    def __init__(self, leader_id: _Optional[int] = ..., time: _Optional[float] = ...) -> None: ...

class VoteRequest(_message.Message):
    __slots__ = ("term", "candidate_id", "last_log_idx", "last_log_term")
    TERM_FIELD_NUMBER: _ClassVar[int]
    CANDIDATE_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_IDX_FIELD_NUMBER: _ClassVar[int]
    LAST_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    term: int
    candidate_id: int
    last_log_idx: int
    last_log_term: int
    def __init__(self, term: _Optional[int] = ..., candidate_id: _Optional[int] = ..., last_log_idx: _Optional[int] = ..., last_log_term: _Optional[int] = ...) -> None: ...

class VoteResponse(_message.Message):
    __slots__ = ("term", "vote_granted", "remaining_lease")
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTE_GRANTED_FIELD_NUMBER: _ClassVar[int]
    REMAINING_LEASE_FIELD_NUMBER: _ClassVar[int]
    term: int
    vote_granted: bool
    remaining_lease: float
    def __init__(self, term: _Optional[int] = ..., vote_granted: bool = ..., remaining_lease: _Optional[float] = ...) -> None: ...
