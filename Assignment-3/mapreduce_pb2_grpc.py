# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import mapreduce_pb2 as mapreduce__pb2


class MasterStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.MapDone = channel.unary_unary(
                '/Master/MapDone',
                request_serializer=mapreduce__pb2.DoneRequest.SerializeToString,
                response_deserializer=mapreduce__pb2.Response.FromString,
                )
        self.ReduceDone = channel.unary_unary(
                '/Master/ReduceDone',
                request_serializer=mapreduce__pb2.DoneRequest.SerializeToString,
                response_deserializer=mapreduce__pb2.Response.FromString,
                )


class MasterServicer(object):
    """Missing associated documentation comment in .proto file."""

    def MapDone(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def ReduceDone(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MasterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'MapDone': grpc.unary_unary_rpc_method_handler(
                    servicer.MapDone,
                    request_deserializer=mapreduce__pb2.DoneRequest.FromString,
                    response_serializer=mapreduce__pb2.Response.SerializeToString,
            ),
            'ReduceDone': grpc.unary_unary_rpc_method_handler(
                    servicer.ReduceDone,
                    request_deserializer=mapreduce__pb2.DoneRequest.FromString,
                    response_serializer=mapreduce__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Master', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Master(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def MapDone(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Master/MapDone',
            mapreduce__pb2.DoneRequest.SerializeToString,
            mapreduce__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def ReduceDone(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Master/ReduceDone',
            mapreduce__pb2.DoneRequest.SerializeToString,
            mapreduce__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class MapperStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Map = channel.unary_unary(
                '/Mapper/Map',
                request_serializer=mapreduce__pb2.MapRequest.SerializeToString,
                response_deserializer=mapreduce__pb2.Response.FromString,
                )
        self.GetPartition = channel.unary_unary(
                '/Mapper/GetPartition',
                request_serializer=mapreduce__pb2.PartitionRequest.SerializeToString,
                response_deserializer=mapreduce__pb2.PartitionResponse.FromString,
                )
        self.Ping = channel.unary_unary(
                '/Mapper/Ping',
                request_serializer=mapreduce__pb2.Empty.SerializeToString,
                response_deserializer=mapreduce__pb2.Response.FromString,
                )


class MapperServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Map(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetPartition(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Ping(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_MapperServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Map': grpc.unary_unary_rpc_method_handler(
                    servicer.Map,
                    request_deserializer=mapreduce__pb2.MapRequest.FromString,
                    response_serializer=mapreduce__pb2.Response.SerializeToString,
            ),
            'GetPartition': grpc.unary_unary_rpc_method_handler(
                    servicer.GetPartition,
                    request_deserializer=mapreduce__pb2.PartitionRequest.FromString,
                    response_serializer=mapreduce__pb2.PartitionResponse.SerializeToString,
            ),
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=mapreduce__pb2.Empty.FromString,
                    response_serializer=mapreduce__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Mapper', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Mapper(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Map(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Mapper/Map',
            mapreduce__pb2.MapRequest.SerializeToString,
            mapreduce__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetPartition(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Mapper/GetPartition',
            mapreduce__pb2.PartitionRequest.SerializeToString,
            mapreduce__pb2.PartitionResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Mapper/Ping',
            mapreduce__pb2.Empty.SerializeToString,
            mapreduce__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class ReducerStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Reduce = channel.unary_unary(
                '/Reducer/Reduce',
                request_serializer=mapreduce__pb2.ReduceRequest.SerializeToString,
                response_deserializer=mapreduce__pb2.Response.FromString,
                )
        self.GetCentroid = channel.unary_unary(
                '/Reducer/GetCentroid',
                request_serializer=mapreduce__pb2.Empty.SerializeToString,
                response_deserializer=mapreduce__pb2.CentroidResult.FromString,
                )
        self.Ping = channel.unary_unary(
                '/Reducer/Ping',
                request_serializer=mapreduce__pb2.Empty.SerializeToString,
                response_deserializer=mapreduce__pb2.Response.FromString,
                )


class ReducerServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Reduce(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetCentroid(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Ping(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ReducerServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Reduce': grpc.unary_unary_rpc_method_handler(
                    servicer.Reduce,
                    request_deserializer=mapreduce__pb2.ReduceRequest.FromString,
                    response_serializer=mapreduce__pb2.Response.SerializeToString,
            ),
            'GetCentroid': grpc.unary_unary_rpc_method_handler(
                    servicer.GetCentroid,
                    request_deserializer=mapreduce__pb2.Empty.FromString,
                    response_serializer=mapreduce__pb2.CentroidResult.SerializeToString,
            ),
            'Ping': grpc.unary_unary_rpc_method_handler(
                    servicer.Ping,
                    request_deserializer=mapreduce__pb2.Empty.FromString,
                    response_serializer=mapreduce__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'Reducer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class Reducer(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Reduce(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Reducer/Reduce',
            mapreduce__pb2.ReduceRequest.SerializeToString,
            mapreduce__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetCentroid(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Reducer/GetCentroid',
            mapreduce__pb2.Empty.SerializeToString,
            mapreduce__pb2.CentroidResult.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def Ping(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/Reducer/Ping',
            mapreduce__pb2.Empty.SerializeToString,
            mapreduce__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
