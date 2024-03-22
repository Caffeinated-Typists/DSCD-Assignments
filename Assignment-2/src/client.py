import os
import grpc
from random import randint

import raft_pb2
import raft_pb2_grpc

NODES = os.environ["NODES"].split(',')
RAFT_PORT = os.environ["RAFT_PORT"]

stubs = dict()

if __name__ == "__main__":
    try:
        # create stubs for all peers
        for node in NODES:
            channel = grpc.insecure_channel(f"{node}:{RAFT_PORT}")
            stub = raft_pb2_grpc.RaftStub(channel)
            stubs[node] = stub
    except:
        print("failed to create stubs")

    stub = [x for x in stubs.values()][randint(0, len(NODES))]

    request = raft_pb2.DataRequest()
    request.data.cmd = raft_pb2.Log.SET
    request.data.key = "abc"
    request.data.value = "def"

    response = stub.RequestData(request)
    print(response)
