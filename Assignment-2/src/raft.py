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
        # persistent state on all servers
        self.current_term:int = 0
        self.voted_for = None
        self.log:list[raft_pb2.Log] = [raft_pb2.Log()] # log entries; each entry contains command for state machine, and term when entry was received by leader (first index is 1)
        
        # volatile state on all servers 
        self.commit_index:int = 0 # index of highest log entry known to be committed (initialized to 0, increases monotonically)
        self.last_applied:int = 0 # index of highest log entry applied to state machine (initialized to 0, increases monotonically)

        # leader specific volatile state, reinitialized after election
        self.next_index:dict = dict() # for each server, index of the next log entry to send to that server (initialized to leader last log index + 1)
        self.match_index:dict = dict()

        # leader id
        self.leader_id = None

        # heatbeat timer
        self.election_timeout = randint(5, 10)
        self.curr_timeout = time()
  
    def leader_loop(self):
        # send AppendEntries RPCs to all peers
        # may have to be rewritten to be done in parallel
        for id, peer in enumerate(NODES):
            if id == ID:
                continue
            print(f"Sending AppendEntries to {peer}")
            request:raft_pb2.AppendEntriesRequest = raft_pb2.AppendEntriesRequest()
            request.term = self.current_term
            request.leader_id = ID
            request.prev_log_idx = len(self.log) - 1
            request.prev_log_term = self.log[-1].term
            request.leader_commit_idx = self.commit_index
            request.entries.extend(self.log[self.next_index.get(peer, 0):])
            response = stubs[peer].AppendEntries(request)
            if response.success:
                self.next_index[peer] = len(self.log)
                self.match_index[peer] = len(self.log) - 1
            else:
                pass

        # if there exists an N such that N > commit_index, a majority of match_index[i] >= N, and log[N].term == current_term, set commit_index = N
        for i in range(len(self.log) - 1, self.commit_index, -1):
            if self.log[i].term == self.current_term:
                count = 0
                for peer in NODES:
                    if self.match_index[peer] >= i:
                        count += 1
                if count > len(NODES) // 2:
                    self.commit_index = i
                    break
        
        sleep(1)
        
    def follower_loop(self):
        # maintain a timer for election timeout
        while (time() - self.curr_timeout) < self.election_timeout:
            pass

        # convert to candidate
        print(f"Node {ID} converting to candidate")
        self.current_term += 1
        self.voted_for = ID
        votes = 1
        request:raft_pb2.VoteRequest = raft_pb2.VoteRequest()
        request.term = self.current_term
        request.candidate_id = ID
        request.last_log_idx = len(self.log) - 1
        request.last_log_term = self.log[-1].term
        for id, peer in enumerate(NODES):
            if id == ID:
                continue
            print(f"Sending RequestVote to {peer}")
            response = stubs[peer].RequestVote(request)
            if response.vote_granted:
                votes += 1
            if votes > len(NODES) // 2:
                self.leader_id = ID
                return
        
    

    def main_loop(self):
        while True:
            if self.leader_id == ID:
                self.leader_loop()
            else:
                self.follower_loop()

    def run(self):
        threading.Thread(target=self.main_loop).start()


    def is_up_to_date(self, last_log_term:int, last_log_index:int)->bool:
        if last_log_term > self.log[-1].term:
            return True
        elif last_log_term == self.log[-1].term and last_log_index >= len(self.log) - 1:
            return True
        return False


    # RPC methods
    def RequestVote(self, request:raft_pb2.VoteRequest, context):
        print(f"Received RequestVote from {request.candidate_id}")
        response:raft_pb2.VoteResponse = raft_pb2.VoteResponse()

        # if request.term < current_term, return false
        if request.term < self.current_term:
            response.term = self.current_term
            response.vote_granted = False
            return response
        
        # if voted_for is None or candidate_id, and candidate's log is at least as up-to-date as receiver's log, grant vote
        if (self.voted_for is None or self.voted_for == request.candidate_id) and self.is_up_to_date(request.last_log_term, request.last_log_idx):
            self.voted_for = request.candidate_id
            response.term = self.current_term
            response.vote_granted = True
            return response

        response.term = self.current_term
        response.vote_granted = False
        return response

    def AppendEntries(self, request:raft_pb2.AppendEntriesRequest, context):
        print(f"Received AppendEntries from {request.leader_id}")
        response:raft_pb2.AppendEntriesResponse = raft_pb2.AppendEntriesResponse()

        if request.term < self.current_term:
            response.term = self.current_term
            response.success = False
            return response

        # if log doesn't contain an entry at prev_log_idx whose term matches prev_log_term
        if len(self.log) < request.prev_log_idx or self.log[request.prev_log_idx].term != request.prev_log_term:
            response.term = self.current_term
            response.success = False
            return response

        # refresh heartbeat timer
        self.curr_timeout = time()


        # if an existing entry conflicts with a new one (same index but different terms)
        if len(self.log) > request.prev_log_idx and self.log[request.prev_log_idx].term != request.prev_log_term:
            self.log = self.log[:request.prev_log_idx]

        # append any new entries not already in the log
        self.log.extend(request.entries)

        # if leader_commit > commit_index, set commit_index = min(leader_commit, index of last new entry)
        if request.leader_commit_idx > self.commit_index:
            self.commit_index = min(request.leader_commit_idx, len(self.log) - 1)

        response.term = self.current_term
        response.success = True
        return response


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
        sleep(1)
        # create stubs for all peers
        for node in NODES:
            channel = grpc.insecure_channel(f"{node}:{RAFT_PORT}")
            stub = raft_pb2_grpc.RaftStub(channel)
            stubs[node] = stub
        raft_servicer.run()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)

