import json
import grpc
from concurrent import futures
from random import randint
from time import time
from time import sleep

import raft_pb2
import raft_pb2_grpc

nodes = ["10.0.1.1", "10.0.1.2", "10.0.1.3", "10.0.1.4", "10.0.1.5"]
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
        
        return True
    
    # RPC methods
    def RequestVote(self, request, context):
        return super().RequestVote(request, context)

    def AppendEntries(self, request, context):
        return super().AppendEntries(request, context)

    def SendHeartbeat(self, request, context):
        return super().SendHeartbeat(request, context)

class DatabaseServicer(raft_pb2_grpc.DatabaseServicer):
    def __init__(self):
        self.data:dict
        try:
            with open("db.json", "r") as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data[str:str] = dict()
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
    raft_pb2_grpc.add_RaftServicer_to_server(raft_servicer, server)
    server.add_insecure_port(f"[::]:{4444}")
    try:
        server.start()
        sleep(15)
        # create stubs for all peers
        for node in nodes:
            channel = grpc.insecure_channel(node + ":4444")
            stub = raft_pb2_grpc.RaftStub(channel)
            stubs[node] = stub
        raft_servicer.run()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)

