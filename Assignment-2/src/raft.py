import os
import json
import grpc
from concurrent import futures
from random import randint
from time import time
from time import sleep
import threading

import raft_pb2
import raft_pb2_grpc

ID = int(os.environ["ID"])
NODES = os.environ["NODES"].split(',')
RAFT_PORT = os.environ["RAFT_PORT"]

RPC_TIMEOUT:float = 0.15 # seconds
ELECTION_TIMEOUT_MIN:int = 5
ELECTION_TIMEOUT_MAX:int = 10
HEARTBEAT_PERIOD:int = 1
LEASE_TIMEOUT:int = 7

stubs = dict()

class Database:
    def __init__(self):
        self.data:dict = dict()
        self.logs:list[raft_pb2.Log] = [raft_pb2.Log()]
        try:
            with open("logs.txt", "r") as f:
                self.logs = json.loads(f.read())
            for log in self.logs:
                if log.cmd is raft_pb2.Log.SET:
                    self.set(log.key, log.value)
        except FileNotFoundError:
            pass
        except Exception as e:
            raise e

    def __str__(self):
        return f"data: {self.data}"
    
    def handle_incoming_log(self, log:raft_pb2.Log)->bool:
        self.logs.append(log)
        if log.cmd is raft_pb2.Log.SET:
            self.set(log.key, log.value)
        self.dump_data()
        return True
    
    def get(self, key)->str:
        return self.data.get(key, "")
    
    def set(self, key:str, val:str) -> bool:
        self.data[key] = val
        return True
    
    def dump_data(self)->None:
        with open("logs.txt", "w") as f:
            f.write(json.dumps(self.data))

class RaftServicer(raft_pb2_grpc.RaftServicer):

    def __init__(self):
        super()
        # persistent state on all servers
        self.current_term:int = 0
        self.voted_for = None
        self.log:list[raft_pb2.Log] = [raft_pb2.Log(term=1)] # log entries; each entry contains command for state machine, and term when entry was received by leader (first index is 1)
        
        # volatile state on all servers 
        self.commit_index:int = 0 # index of highest log entry known to be committed (initialized to 0, increases monotonically)
        self.last_applied:int = 0 # index of highest log entry applied to state machine (initialized to 0, increases monotonically)
        self.leader_lease = raft_pb2.Lease(leader_id=-1)

        # leader specific volatile state, reinitialized after election
        self.next_index:dict = dict() # for each server, index of the next log entry to send to that server (initialized to leader last log index + 1)
        self.match_index:dict = dict() # for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically)

        # leader id
        self.leader_id = None

        # heatbeat timer
        self.election_timeout:int = randint(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.curr_timeout = time()

        self.votes = 0

        self.db = Database()
  
    def leader_loop(self):
        # send AppendEntries RPCs to all peers
        # may have to be rewritten to be done in parallel
        nodes_updated = 1
        request:raft_pb2.AppendEntriesRequest = raft_pb2.AppendEntriesRequest()
        request.term = self.current_term
        request.leader_id = ID
        request.prev_log_idx = len(self.log) - 1
        request.prev_log_term = self.log[-1].term
        request.leader_commit_idx = self.commit_index
        if (time() - self.leader_lease.time) < LEASE_TIMEOUT and self.leader_lease.leader_id != ID:
            request.leader_lease.leader_id = -1 
        else:
            request.leader_lease.leader_id = ID
            request.leader_lease.time = time()
            self.leader_lease.CopyFrom(request.leader_lease)
        for id, peer in enumerate(NODES):
            if id == ID:
                continue
            print(f"Sending AppendEntries to {peer}")
            request.ClearField("entries")
            request.entries.extend(self.log[self.next_index.get(peer, 1):])
            try:
                response = stubs[peer].AppendEntries(request, timeout=RPC_TIMEOUT)
                if response.success:
                    self.next_index[peer] = len(self.log)
                    self.match_index[peer] = len(self.log) - 1
                    nodes_updated += 1
            except grpc.RpcError:
                pass
            except Exception as e:
                raise e
            
        # if nodes_updated <= len(NODES) // 2:
        #     self.leader_id = None
        #     return

        # if there exists an N such that N > commit_index, a majority of match_index[i] >= N, and log[N].term == current_term, set commit_index = N
        for i in range(len(self.log) - 1, self.commit_index, -1):
            if self.log[i].term == self.current_term:
                count = 0
                for peer in NODES:
                    if self.match_index.get(peer, -1) >= i:
                        count += 1
                if count > len(NODES) // 2:
                    self.commit_index = i
                    break

        for i in range(self.last_applied, self.commit_index + 1):
            self.db.handle_incoming_log(self.log[i])
        self.last_applied = self.commit_index

        sleep(HEARTBEAT_PERIOD)
        
    def follower_loop(self):
        # maintain a timer for election timeout
        while (time() - self.curr_timeout) < self.election_timeout:
            sleep(0.5 * HEARTBEAT_PERIOD)
        
        vote_cond = threading.Condition()

        def subroutine(request, peer):
            try:
                response = stubs[peer].RequestVote(request, timeout=RPC_TIMEOUT)
                if response.vote_granted:
                    with vote_cond:
                        self.votes += 1
                        if self.votes > len(NODES) // 2:
                            self.leader_id = ID
                            vote_cond.notify_all()
            except grpc.RpcError:
                pass
            except Exception as e:
                raise e


        # convert to candidate
        print(f"Node {ID} converting to candidate")
        self.current_term += 1
        self.election_timeout = randint(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.voted_for = ID
        self.votes = 1
        request:raft_pb2.VoteRequest = raft_pb2.VoteRequest()
        request.term = self.current_term
        request.candidate_id = ID
        request.last_log_idx = len(self.log) - 1
        request.last_log_term = self.log[-1].term
        thrds:list[threading.Thread] = []
        for id, peer in enumerate(NODES):
            if id == ID:
                continue
            print(f"Sending RequestVote to {peer}")
            thrds.append(threading.Thread(target=subroutine, args=(request, peer)))    

        for t in thrds:
            t.start()

        with vote_cond:
            while self.votes <= len(NODES) // 2:
                vote_cond.wait()

        for t in thrds:
            t.join()

        # after the candidate is elected, check leader_lease
                

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
        return True


    # RPC methods
    def RequestVote(self, request:raft_pb2.VoteRequest, context):
        response:raft_pb2.VoteResponse = raft_pb2.VoteResponse()

        # if request.term < current_term, return false
        if (request.term < self.current_term):
            print(f"Received RequestVote from {request.candidate_id} : Sent False, request.term < current_term")  
            response.term = self.current_term
            response.vote_granted = False
            return response
        
        # if voted_for is None or candidate_id, and candidate's log is at least as up-to-date as receiver's log, grant vote
        if self.is_up_to_date(request.last_log_term, request.last_log_idx):
            if request.term > self.current_term or self.voted_for is None or self.voted_for == request.candidate_id:
                print(f"Received RequestVote from {request.candidate_id} : Sent True")
                response.term = self.current_term
                response.vote_granted = True
                self.voted_for = request.candidate_id
                return response

        print(f"Received RequestVote from {request.candidate_id} : Sent False, voted_for is not None or candidate_id, and candidate's log is not at least as up-to-date as receiver's log")
        response.term = self.current_term
        response.vote_granted = False
        return response

    def AppendEntries(self, request:raft_pb2.AppendEntriesRequest, context):
        print(f"Received AppendEntries from {request.leader_id}")
        response:raft_pb2.AppendEntriesResponse = raft_pb2.AppendEntriesResponse()

        if request.term < self.current_term:
            print(f"Received AppendEntries from {request.leader_id}: Sent False")
            response.term = self.current_term
            response.success = False
            return response

        # if log doesn't contain an entry at prev_log_idx whose term matches prev_log_term
        if len(self.log) > request.prev_log_idx and self.log[request.prev_log_idx].term != request.prev_log_term:
            print(f"Received AppendEntries from {request.leader_id}: Sent False, log doesn't contain an entry at prev_log_idx whose term matches prev_log_term")
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

        print(f"Received AppendEntries from {request.leader_id}: Sent True")
        response.term = self.current_term
        response.success = True
        self.leader_id = request.leader_id
        if (request.leader_lease.leader_id != -1):
            self.leader_lease.CopyFrom(request.leader_lease)
        print(self.leader_lease)
        return response


    def RequestData(self, request, context):
        print(f"Received RequestData from {context.peer()}")
        response = raft_pb2.DataResponse()
        if self.leader_id == None:
            response.leader_id = -1
            return response

        response.leader_id = self.leader_id
        if self.leader_id == ID:
            if request.data.cmd == raft_pb2.Log.GET:
                response.status = True
                response.data.key = request.data.key
                response.data.value = self.db.get(request.data.key)
            elif request.data.cmd == raft_pb2.Log.SET:
                if self.leader_lease.leader_id != ID:
                    response.status = False
                    print(self.leader_lease)
                    return response
                response.status = True
                log = raft_pb2.Log()
                log.cmd = raft_pb2.Log.SET
                log.key = request.data.key
                log.value = request.data.value
                log.term = self.current_term
                self.log.append(log)
        return response


if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_servicer = RaftServicer()
    raft_pb2_grpc.add_RaftServicer_to_server(raft_servicer, server)
    server.add_insecure_port(f"[::]:{RAFT_PORT}")
    try:
        server.start()
        sleep(1) # wait for server to start
        # create stubs for all peers
        for node in NODES:
            channel = grpc.insecure_channel(f"{node}:{RAFT_PORT}")
            stub = raft_pb2_grpc.RaftStub(channel)
            stubs[node] = stub
        raft_servicer.run()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)

