import grpc
from concurrent import futures

from proto import mapreduce_pb2
from proto import mapreduce_pb2_grpc

PORT_MASTER:int = 4444

class MasterServicer(mapreduce_pb2_grpc.MasterServicer):
    def MapDone(self, request, context):
        return super().MapDone(request, context)

    def ReduceDone(self, request, context):
        return super().ReduceDone(request, context)


if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mapreduce_pb2_grpc.add_MasterServicer_to_server(MasterServicer(), server)
    server.add_insecure_port(f"[::]:{PORT_MASTER}")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)
