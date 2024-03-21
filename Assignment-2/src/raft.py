import os
import json
import grpc
from concurrent import futures
from random import randint
from time import time
from time import sleep
import threading
from urllib.parse import unquote

import raft_pb2
import raft_pb2_grpc

ID = int(os.environ["ID"])
NODES = os.environ["NODES"].split(',')
RAFT_PORT = os.environ["RAFT_PORT"]
DB_PORT = os.environ["DB_PORT"]

stubs = dict()

class RaftServicer(raft_pb2_grpc.RaftServicer):

    def __init__(self):
        super()
        # TODO: add node identifier
        self.term:int = 0
        self.voted_for:int = -1
        self.votes = set()
        self.state:str = "FOLLOWER"
        self.leader_id:int = -1
        self.commit_idx:int = 0
        self.server_idx:int = -1

        self.lease_timeout:float = 0
        self.election_timeout:float = -1

        self.election_period_ms = randint(1000, 5000)


    def run(self):
        self.set_election_timeout()

    def set_election_timeout(self, timeout=None):
        if timeout:
            self.election_timeout = timeout
        else:
            self.election_timeout = time() + randint(self.election_period_ms, 2 * self.election_period_ms) / 1000.0

    def on_election_timeout(self):
        while True:
            if time() > self.election_timeout and (self.state in ["FOLLOWER", "CANDIDATE"]):
                self.set_election_timeout()
                self.start_election()

    def start_election(self):
        self.state = "CANDIDATE"
        self.voted_for = self.server_idx
        self.term += 1
        self.votes.add(self.server_idx)

        # TODO: send RequestVote RPC to everyone
        def make_rpc_call(stub):
            request = raft_pb2.VoteRequest()
            request.term = self.term
            request.candidate_id = ID
            request.last_log_idx = -1
            request.last_log_term = -1

            while True:
                if self.state == 'CANDIDATE' and time() < self.election_timeout:
                    response = stub.RequestVote(request)

        threads = list()
        for node,stub in stubs.items():
            if node != NODES[ID]:
                threads.append(threading.Thread(target=make_rpc_call, args=(stub,)))
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.stop()
        
        return True
    
    def step_down(self, term):
        self.term = term
        self.state = 'FOLLOWER'
        self.voted_for = -1
        self.set_election_timeout()
    
    # RPC methods
    def RequestVote(self, request, context):
        node = unquote(context.peer())
        node_id = -1 # node # TODO: translate from node ip to id
        if request.term > self.term:
            self.step_down(request.term)

        self.last_log_term = -1 
        self.last_log_idx = -1 

        if request.term == self.term \
            and (self.voted_for == node_id or self.voted_for == -1) \
            and (request.last_log_term == self.last_log_term and request.last_log_idx >= self.last_log_idx):
                self.voted_for = node_id
                self.state = 'FOLLOWER'
                self.set_election_timeout()
        
        response = raft_pb2.VoteResponse()
        response.term = self.term
        response.vote_granted = True
        return response

    def AppendEntries(self, request, context):
        return super().AppendEntries(request, context)

    def SendHeartbeat(self, request, context):
        return super().SendHeartbeat(request, context)

class DatabaseServicer(raft_pb2_grpc.DatabaseServicer):
    def __init__(self):
        self.data:dict = dict()
        try:
            with open("db.json", "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = dict()
        except Exception as e:
            raise e

    def __str__(self):
        return f"data: {self.data}"
    
    def get(self, key)->str:
        return self.data.get(key, None)
    
    def set(self, key:str, value:str) -> bool:
        self.data[key] = value
        self.dump_data()
        return True
    
    def dump_data(self)->None:
        with open("db.json", "w") as f:
            json.dump(self.data, f)

    def RequestData(self, request, context):
        return super().RequestData(request, context)

if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_servicer = RaftServicer()
    db_servicer = DatabaseServicer()
    raft_pb2_grpc.add_RaftServicer_to_server(raft_servicer, server)
    raft_pb2_grpc.add_DatabaseServicer_to_server(db_servicer, server)
    server.add_insecure_port(f"[::]:{RAFT_PORT}")
    server.add_insecure_port(f"[::]:{DB_PORT}")
    try:
        server.start()
        sleep(5)
        # create stubs for all peers
        for node in NODES:
            channel = grpc.insecure_channel(node + RAFT_PORT)
            stub = raft_pb2_grpc.RaftStub(channel)
            stubs[node] = stub
        raft_servicer.run()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)

