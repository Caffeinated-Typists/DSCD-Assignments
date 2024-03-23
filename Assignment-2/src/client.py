import os
import sys
import grpc

import raft_pb2
import raft_pb2_grpc

NODES = os.environ["NODES"].split(',')
RAFT_PORT = os.environ["RAFT_PORT"]

if __name__ == "__main__":
    node = NODES[int(sys.argv[1])]
    channel = grpc.insecure_channel(f"{node}:{RAFT_PORT}")
    stub = raft_pb2_grpc.RaftStub(channel)

    request = raft_pb2.DataRequest()
    request.data.cmd = raft_pb2.Log.SET
    request.data.key = "abc"
    request.data.value = "def"

    response = stub.RequestData(request)
    print(response)
