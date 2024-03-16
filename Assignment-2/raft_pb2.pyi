from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ("status", "info")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    status: int
    info: str
    def __init__(self, status: _Optional[int] = ..., info: _Optional[str] = ...) -> None: ...

class DbRequest(_message.Message):
    __slots__ = ("type", "data")
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    type: int
    data: Log
    def __init__(self, type: _Optional[int] = ..., data: _Optional[_Union[Log, _Mapping]] = ...) -> None: ...

class DbResponse(_message.Message):
    __slots__ = ("status", "data")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    status: int
    data: Log
    def __init__(self, status: _Optional[int] = ..., data: _Optional[_Union[Log, _Mapping]] = ...) -> None: ...

class AppendEntriesRequest(_message.Message):
    __slots__ = ("term", "leader_id", "prev_log_idx", "prev_log_term", "leader_commit_idx", "data")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_IDX_FIELD_NUMBER: _ClassVar[int]
    PREV_LOG_TERM_FIELD_NUMBER: _ClassVar[int]
    LEADER_COMMIT_IDX_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    term: int
    leader_id: int
    prev_log_idx: int
    prev_log_term: int
    leader_commit_idx: int
    data: Log
    def __init__(self, term: _Optional[int] = ..., leader_id: _Optional[int] = ..., prev_log_idx: _Optional[int] = ..., prev_log_term: _Optional[int] = ..., leader_commit_idx: _Optional[int] = ..., data: _Optional[_Union[Log, _Mapping]] = ...) -> None: ...

class AppendEntriesResponse(_message.Message):
    __slots__ = ("term", "success")
    TERM_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    term: int
    success: bool
    def __init__(self, term: _Optional[int] = ..., success: bool = ...) -> None: ...

class Heartbeat(_message.Message):
    __slots__ = ("term", "lease_time")
    TERM_FIELD_NUMBER: _ClassVar[int]
    LEASE_TIME_FIELD_NUMBER: _ClassVar[int]
    term: int
    lease_time: int
    def __init__(self, term: _Optional[int] = ..., lease_time: _Optional[int] = ...) -> None: ...

class InstallSnapshot(_message.Message):
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

class Log(_message.Message):
    __slots__ = ("key", "value")
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: int
    value: int
    def __init__(self, key: _Optional[int] = ..., value: _Optional[int] = ...) -> None: ...

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
    __slots__ = ("term", "vote_granted")
    TERM_FIELD_NUMBER: _ClassVar[int]
    VOTE_GRANTED_FIELD_NUMBER: _ClassVar[int]
    term: int
    vote_granted: bool
    def __init__(self, term: _Optional[int] = ..., vote_granted: bool = ...) -> None: ...
