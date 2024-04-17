from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class MapRequest(_message.Message):
    __slots__ = ("id", "start", "end", "reducers", "centroids")
    ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REDUCERS_FIELD_NUMBER: _ClassVar[int]
    CENTROIDS_FIELD_NUMBER: _ClassVar[int]
    id: int
    start: int
    end: int
    reducers: int
    centroids: _containers.RepeatedScalarFieldContainer[float]
    def __init__(self, id: _Optional[int] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., reducers: _Optional[int] = ..., centroids: _Optional[_Iterable[float]] = ...) -> None: ...

class PartitionRequest(_message.Message):
    __slots__ = ("idx",)
    IDX_FIELD_NUMBER: _ClassVar[int]
    idx: int
    def __init__(self, idx: _Optional[int] = ...) -> None: ...

class PartitionResponse(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: bytes
    def __init__(self, data: _Optional[bytes] = ...) -> None: ...

class ReduceRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
