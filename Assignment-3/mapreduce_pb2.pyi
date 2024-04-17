from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Response(_message.Message):
    __slots__ = ("status",)
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: bool
    def __init__(self, status: bool = ...) -> None: ...

class DoneRequest(_message.Message):
    __slots__ = ("id", "status")
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: int
    status: bool
    def __init__(self, id: _Optional[int] = ..., status: bool = ...) -> None: ...

class MapRequest(_message.Message):
    __slots__ = ("id", "start", "end", "reducers")
    ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    REDUCERS_FIELD_NUMBER: _ClassVar[int]
    id: int
    start: int
    end: int
    reducers: int
    def __init__(self, id: _Optional[int] = ..., start: _Optional[int] = ..., end: _Optional[int] = ..., reducers: _Optional[int] = ...) -> None: ...

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
    __slots__ = ("id", "partition_idx", "mappers")
    ID_FIELD_NUMBER: _ClassVar[int]
    PARTITION_IDX_FIELD_NUMBER: _ClassVar[int]
    MAPPERS_FIELD_NUMBER: _ClassVar[int]
    id: int
    partition_idx: int
    mappers: int
    def __init__(self, id: _Optional[int] = ..., partition_idx: _Optional[int] = ..., mappers: _Optional[int] = ...) -> None: ...

class CentroidRequest(_message.Message):
    __slots__ = ("id",)
    ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    def __init__(self, id: _Optional[int] = ...) -> None: ...

class CentroidResult(_message.Message):
    __slots__ = ("status", "data")
    STATUS_FIELD_NUMBER: _ClassVar[int]
    DATA_FIELD_NUMBER: _ClassVar[int]
    status: bool
    data: bytes
    def __init__(self, status: bool = ..., data: _Optional[bytes] = ...) -> None: ...

class Empty(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...
