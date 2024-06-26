import os
import sys
import grpc
import random
from time import time

import raft_pb2
import raft_pb2_grpc

NODES = os.environ["NODES"].split(',')
RAFT_PORT = os.environ["RAFT_PORT"]
REQ_TIMEOUT:int = 5
MAX_RETRIES:int = 20

if __name__ == "__main__":
    if len(sys.argv) < 3 or (sys.argv[1] == 'set' and len(sys.argv) < 4):
        print(f"usage: {sys.argv[0]}  <set|get> <key> <value>")
        exit()

    try:
        with open('client_leader_id', 'r') as f:
            node_id = int(f.read())
    except FileNotFoundError or EOFError:
        node_id = random.randint(0, len(NODES) - 1) 


    cmd = sys.argv[1] 
    key = sys.argv[2]
    val = sys.argv[3] if cmd == 'set' else ''

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

    
    response: raft_pb2.DataResponse = raft_pb2.DataResponse()
    response.status = False
    response.leader_id = node_id

    got_response_from = [False for _ in range(len(NODES))]


    for _ in range(MAX_RETRIES):
        if response.leader_id != -1:
            node_id = response.leader_id
        else:
            node_id = random.randint(0, len(NODES) - 1)

        node = NODES[node_id]
        channel = grpc.insecure_channel(f"{node}:{RAFT_PORT}")
        stub = raft_pb2_grpc.RaftStub(channel)
        

        try:
            response = stub.RequestData(request, timeout=REQ_TIMEOUT)
            if response.status:
                break
        except grpc.RpcError as e:
            print(f"Error: Could not connect to {node}!")
            response.leader_id = -1

        got_response_from[node_id] = True

        if all(got_response_from):
            break


    with open('client_leader_id', 'w') as f:
        f.write(str(node_id))

    print(response)
    print(f"Time: {time()}")
