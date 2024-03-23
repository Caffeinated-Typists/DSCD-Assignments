import os
import sys
import grpc

import raft_pb2
import raft_pb2_grpc

NODES = os.environ["NODES"].split(',')
RAFT_PORT = os.environ["RAFT_PORT"]

if __name__ == "__main__":
    if len(sys.argv) < 4 or (sys.argv[2] == 'set' and len(sys.argv) < 5):
        print(f"usage: {sys.argv[0]} <node_id> <set|get> <key> <value>")
        exit()

    node_id = int(sys.argv[1])
    cmd = sys.argv[2] 
    key = sys.argv[3]
    val = sys.argv[4] if cmd == 'set' else ''

    node = NODES[node_id]
    channel = grpc.insecure_channel(f"{node}:{RAFT_PORT}")
    stub = raft_pb2_grpc.RaftStub(channel)

    request = raft_pb2.DataRequest()

    if cmd == 'set':
        request.data.cmd = raft_pb2.Log.SET
        request.data.key = key
        request.data.value = val
    elif cmd == 'get':
        request.data.cmd = raft_pb2.Log.GET
        request.data.key = key
    else:
        print('error: only set & get actions are supported!')
        exit()

    response = stub.RequestData(request)
    print(f"status: {response.status}")
    print(f"leader_id: {response.leader_id}")

    if response.status == True and response.leader_id == node_id:
        print(response.data)
