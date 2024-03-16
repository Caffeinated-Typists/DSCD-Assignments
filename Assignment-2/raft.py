import grpc
from concurrent import futures

import raft_pb2
import raft_pb2_grpc

class RaftServicer(raft_pb2_grpc.RaftServicer):
    def RequestVote(self, request, context):
        return super().RequestVote(request, context)

    def AppendEntries(self, request, context):
        return super().AppendEntries(request, context)

    def SendHeartbeat(self, request, context):
        return super().SendHeartbeat(request, context)

class DatabaseServicer(raft_pb2_grpc.DatabaseServicer):
    def RequestData(self, request, context):
        return super().RequestData(request, context)

if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_pb2_grpc.add_RaftServicer_to_server(RaftServicer(), server)
    server.add_insecure_port(f"[::]:{4444}")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)

