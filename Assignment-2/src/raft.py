from typing import Any
import json
import grpc
from concurrent import futures
import threading
from random import randint
from time import time

import raft_pb2
import raft_pb2_grpc

class Raft:

    def __init__(self) -> None:
        self.term:int = 0
        self.voted_for:int = None
        self.lease_timeout:float = 0
        self.election_timeout:float = randint(5, 15)
        self.leader_id:int = None
        self.state:str = "follower"

    def __str__(self):
        return f"term: {self.term}, voted_for: {self.voted_for}, heartbeat_timeout: {self.lease_timeout}, election_timeout: {self.election_timeout}, leader_id: {self.leader_id}, state: {self.state}"
    
    def new_term(self, term:int, state) -> bool:
        # To be used when a new term is triggered
        # Can be triggered by Election timeout, or recieving a higher term in an RPC
        if term <= self.term:
            return False
        self.term = term
        self.voted_for = None
        self.leader_id = None
        self.state = state
        self.election_timeout = randint(5, 15)
        return True

    def change_state(self, state:str) -> None:
        # To be used when a node changes from candidate to leader or follower
        self.state = state

class Database():

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
        
class Election():

    def __init__(self, raft:Raft):
        self.raft:Raft = raft
        self.LAST_HEARTBEAT_TIME:float = time()

    def __str__(self):
        return f"term: {self.term}, candidate_id: {self.candidate_id}, last_log_idx: {self.last_log_idx}, last_log_term: {self.last_log_term}"
    
    def start_election(self) -> bool:
        pass
    
    def send_vote_request(self) -> bool:
        pass

    def send_heartbeat(self) -> bool:
        pass

    def check_lease_timeout(self) -> bool:
        pass

    def check_election_timeout(self) -> bool:
        pass

    def handle_lease_timeout(self) -> bool:
        pass

    def handle_election_timeout(self) -> bool:
        pass

class LogReplication():

    def __init__(self, term, leader_id, prev_log_idx, prev_log_term, leader_commit_idx, data):
        pass

    def __str__(self):
        return f"term: {self.term}, leader_id: {self.leader_id}, prev_log_idx: {self.prev_log_idx}, prev_log_term: {self.prev_log_term}, leader_commit_idx: {self.leader_commit_idx}, data: {self.data}"

class RaftServicer(raft_pb2_grpc.RaftServicer, Raft, Election, LogReplication, Database):

    def __init__(self):
        self.raft:Raft = Raft()
        self.election:Election = Election()
        self.log_replication:LogReplication = LogReplication()
        self.database:Database = Database()

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

