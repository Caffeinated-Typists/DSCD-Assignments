import os
import json
import grpc
import copy
from concurrent import futures
from random import random
from time import time
from time import sleep
import threading
from google.protobuf.json_format import ParseDict, MessageToDict

import logging
logging.basicConfig(filename='dump.txt', level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
logger = logging.getLogger("Raft")

import raft_pb2
import raft_pb2_grpc

ID = int(os.environ["ID"])
NODES = os.environ["NODES"].split(',')
RAFT_PORT = os.environ["RAFT_PORT"]

RPC_TIMEOUT:float = 0.5 # seconds           
ELECTION_TIMEOUT_MIN:int = 8                
ELECTION_TIMEOUT_MAX:int = 15               
HEARTBEAT_PERIOD:int = 1                    
LEASE_TIMEOUT:int = 10

stubs = dict()

rand_time = lambda x, y: x + random() * (y - x)

def print_func_name(func):
    def wrapper(*args, **kwargs):
        print(f"Function '{func.__name__}' is called.")
        return func(*args, **kwargs)
    return wrapper


class Database:
    def __init__(self):
        self.has_meta = False
        self.metadata:dict = {
            "current_term": 0,
            "voted_for": None,
            "commit_index": 0,
        }
        self.data:dict = dict()
        self.logs:list[raft_pb2.Log] = [raft_pb2.Log()]
        try:
            with open("metadata.json", "r") as f:
                self.metadata = json.loads(f.read())
                self.has_meta = True
        except:
            self.has_meta = False

        if not self.has_meta: return
        try:
            with open("log.json", "r") as f:
                logs = json.loads(f.read())
                self.logs = [ParseDict(x, message=raft_pb2.Log()) for x in logs]
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
        self.dump_log()
        if log.cmd is raft_pb2.Log.SET:
            self.set(log.key, log.value)
        return True
    
    def get(self, key)->str:
        return self.data.get(key, "")
    
    def set(self, key:str, val:str) -> bool:
        self.data[key] = val
        return True
    
    def dump_meta(self)->None:
        with open("metadata.json", "w") as f:
            f.write(json.dumps(self.metadata))

    def dump_db(self)->None:
        with open("db.json", "w") as f:
            f.write(json.dumps(self.data))

    def dump_log(self)->None:
        with open("log.json", "w") as f:
            f.write(json.dumps([MessageToDict(x) for x in self.logs]))


class RaftServicer(raft_pb2_grpc.RaftServicer):

    def __init__(self):
        super()

        self.db = Database()

        # persistent state on all servers
        self.current_term:int = 0
        self.voted_for = None
        self.raft_logs:list[raft_pb2.Log] = [raft_pb2.Log(term=0, cmd=raft_pb2.Log.NOOP)] # log entries; each entry contains command for state machine, and term when entry was received by leader (first index is 1)
        
        # volatile state on all servers 
        self.commit_index:int = 0 # index of highest log entry known to be committed (initialized to 0, increases monotonically)
        self.last_applied:int = 0 # index of highest log entry applied to state machine (initialized to 0, increases monotonically)
        self.leader_lease = raft_pb2.Lease(leader_id=-1)

        # leader specific volatile state, reinitialized after election
        self.next_index:dict = dict() # for each server, index of the next log entry to send to that server (initialized to leader last log index + 1)
        self.match_index:dict = dict() # for each server, index of highest log entry known to be replicated on server (initialized to 0, increases monotonically)
        for peer in NODES:
            self.next_index[peer] = 1
            self.match_index[peer] = 0

        # leader id
        self.leader_id = None

        # heatbeat timer
        self.election_timeout:int = rand_time(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.curr_timeout = None

        self.votes = 0

        # locks
        self.voting_lock = threading.Lock()
        self.replication_lock = threading.Lock()
        self.leader_lock = threading.Lock()

        self.lease_timeout_wait:float = 0 # maximum timestamp of old leader's lease, after which new lease can be issued by new leader

        if self.db.has_meta:
            print(self.db)
            self.current_term = self.db.metadata['current_term']
            self.voted_for = self.db.metadata['voted_for']
            self.raft_logs = copy.deepcopy(self.db.logs)
            self.commit_index = self.db.metadata['commit_index']

    def log_replication(self, update_lease:bool = True) -> int:
        """Replicated logs to the follower nodes"""
        with self.replication_lock:
            request:raft_pb2.AppendEntriesRequest = raft_pb2.AppendEntriesRequest()
            request.term = self.current_term
            request.leader_id = ID
            request.prev_log_idx = len(self.raft_logs) - 1
            request.prev_log_term = self.raft_logs[request.prev_log_idx].term
            request.leader_commit_idx = self.commit_index


            if update_lease:
                request.leader_lease.leader_id = ID
                request.leader_lease.time = time()
            else:
                request.leader_lease.leader_id = -1

            nodes_recieved = 1
            for id, peer in enumerate(NODES):
                if id == ID:
                    continue
                print(f"Sending AppendEntries to {peer}")
                request.ClearField("entries")
                #request.entries.extend(self.raft_logs[self.next_index.get(peer, 1):])
                request.prev_log_idx = self.match_index[peer]
                request.prev_log_term = self.raft_logs[request.prev_log_idx].term
                request.entries.extend(self.raft_logs[self.next_index[peer]:])
                try:
                    response = stubs[peer].AppendEntries(request, timeout=RPC_TIMEOUT)
                    if response.success:
                        self.next_index[peer] = len(self.raft_logs)
                        self.match_index[peer] = len(self.raft_logs) - 1
                        nodes_recieved += 1

                    else:
                        if response.term > self.current_term:
                            self.leader_id = None
                        self.next_index[peer] = max(1, self.next_index[peer] - 1)
                    
                except grpc.RpcError as e:
                    print(f"AppendEntriesRequest failed for {id}, {peer}")
                    logger.info(f"Error occurred while sending RPC to Node {ID}")
                except Exception as e:
                    raise e
                
            if nodes_recieved > len(NODES) // 2:
                self.leader_lease.CopyFrom(request.leader_lease)

            # if there exists an N such that N > commit_index, a majority of match_index[i] >= N, and log[N].term == current_term, set commit_index = N
            for i in range(len(self.raft_logs) - 1, self.commit_index, -1):
                if self.raft_logs[i].term == self.current_term:
                    count = 0
                    for peer in NODES:
                        if self.match_index[peer] >= i:
                            count += 1
                    if count > len(NODES) // 2:
                        self.commit_index = i
                        break

            for i in range(self.last_applied + 1, self.commit_index + 1):
                self.db.handle_incoming_log(self.raft_logs[i])
                logger.info(f"Node {ID} (leader) committed the entry {raft_pb2.Log.action.Name(self.raft_logs[i].cmd)} {self.raft_logs[i].key} {self.raft_logs[i].value if self.raft_logs[i].cmd == raft_pb2.Log.SET else ''} to the state machine.")
            self.last_applied = self.commit_index

            self.db.metadata['commit_index'] = self.commit_index
            self.db.metadata['voted_for'] = self.voted_for
            self.db.dump_meta()

            return nodes_recieved



    def leader_loop(self):
        # send AppendEntries RPCs to all peers
        # may have to be rewritten to be done in parallel
        t1 = time()
        
        if ((time() - self.leader_lease.time) > LEASE_TIMEOUT) and (self.leader_lease.leader_id  == ID):
            self.leader_id = None
            self.leader_lease.leader_id = -1
            logger.info(f"Leader {ID} lease renewal failed, Stepping down")
            return
        
        if (time() - self.lease_timeout_wait) < LEASE_TIMEOUT and self.leader_lease.leader_id != ID:
            self.log_replication(update_lease=False)
            logger.info("New Leader waiting for Old Leader Lease to timeout")
        else:
            if self.leader_lease.leader_id != ID:
                self.raft_logs.append(raft_pb2.Log(cmd=raft_pb2.Log.NOOP, term=self.current_term))
            logger.info(f"Leader {ID} sending heartbeat & Renewing Lease")
            self.log_replication()



        sleep(HEARTBEAT_PERIOD)
        
    def follower_loop(self):
        # maintain a timer for election timeout
        while (time() - self.curr_timeout) < self.election_timeout:
            pass
        
        vote_cond = threading.Condition()
        logger.info(f"Node {ID} election timer timed out, Starting election")

        def subroutine(request, peer):
            try:
                response = stubs[peer].RequestVote(request, timeout=RPC_TIMEOUT)
                if response.vote_granted:
                    with vote_cond:
                        self.votes += 1
                        if self.votes > len(NODES) // 2:
                            self.leader_id = ID
                            self.db.metadata["current_term"] = self.current_term
                            self.db.dump_meta()
                            logger.info(f"Node {ID} became the leader for term {self.current_term}")
                            vote_cond.notify_all()
                    self.lease_timeout_wait = max(self.lease_timeout_wait, response.remaining_lease)
            except grpc.RpcError:
                pass
            except Exception as e:
                raise e


        # convert to candidate
        print(f"Node {ID} converting to candidate at time {time()}")
        self.current_term += 1
        print(f"Node {ID} current term: {self.current_term}")
        self.election_timeout = rand_time(ELECTION_TIMEOUT_MIN, ELECTION_TIMEOUT_MAX)
        self.voted_for = ID
        self.votes = 1
        request:raft_pb2.VoteRequest = raft_pb2.VoteRequest()
        request.term = self.current_term
        request.candidate_id = ID
        request.last_log_idx = len(self.raft_logs) - 1
        request.last_log_term = self.raft_logs[request.last_log_idx].term

        self.curr_timeout = time()

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
                if (time() - self.curr_timeout) > self.election_timeout:
                    break
                vote_cond.wait(timeout=1)

        for t in thrds:
            t.join()

        if self.leader_id == ID:
            for peer in NODES:
                self.match_index[peer] = self.commit_index
                self.next_index[peer] = self.commit_index + 1
            self.lease_timeout_wait = max(self.lease_timeout_wait, self.leader_lease.time)



    def main_loop(self):
        while True:
            if self.leader_id == ID:
                self.leader_loop()
            else:
                self.follower_loop()

    def run(self):
        self.curr_timeout = time()
        threading.Thread(target=self.main_loop).start()

    def is_up_to_date(self, last_log_term:int, last_log_index:int)->bool:
        if last_log_term > self.raft_logs[-1].term:
            return True
        elif last_log_term == self.raft_logs[-1].term and last_log_index >= len(self.raft_logs) - 1:
            return True
        return False


    # RPC methods
    def RequestVote(self, request:raft_pb2.VoteRequest, context):
        response:raft_pb2.VoteResponse = raft_pb2.VoteResponse()

        # if request.term < current_term, return false
        if (request.term < self.current_term):
            print(f"Received RequestVote from {request.candidate_id} : Sent False, request.term < current_term")  
            logger.info(f"Vote denied for Node {request.candidate_id} in term {self.current_term + 1}.")
            response.term = self.current_term
            response.vote_granted = False
            return response
        
        # if voted_for is None or candidate_id, and candidate's log is at least as up-to-date as receiver's log, grant vote
        with self.voting_lock:
            # print(self.is_up_to_date(request.last_log_term, request.last_log_idx), self.voted_for, request.candidate_id, self.current_term, request.term)
            if self.is_up_to_date(request.last_log_term, request.last_log_idx):
                if request.term > self.current_term or self.voted_for is None or self.voted_for == request.candidate_id:
                    self.db.metadata["current_term"] = self.current_term
                    self.db.dump_meta()
                    print(f"Received RequestVote from {request.candidate_id} : Sent True")
                    response.term = self.current_term
                    response.vote_granted = True
                    response.remaining_lease = self.leader_lease.time
                    self.voted_for = request.candidate_id
                    self.curr_timeout = time()
                    logger.info(f"Vote granted for Node {request.candidate_id} in term {self.current_term + 1}.")
                    return response

        print(f"Received RequestVote from {request.candidate_id} : Sent False, voted_for is not None or candidate_id, and candidate's log is not at least as up-to-date as receiver's log")
        logger.info(f"Vote denied for Node {request.candidate_id} in term {self.current_term + 1}.")
        response.term = self.current_term
        response.vote_granted = False
        return response

    def AppendEntries(self, request:raft_pb2.AppendEntriesRequest, context):
        print(f"Received AppendEntries from {request.leader_id} at {time()}")
        response:raft_pb2.AppendEntriesResponse = raft_pb2.AppendEntriesResponse()

        if request.term < self.current_term:
            print(f"Received AppendEntries from {request.leader_id}: Sent False")
            logger.info(f"Node {ID} rejected AppendEntries RPC from {self.leader_id}")
            response.term = self.current_term
            response.success = False
            return response

        # if log doesn't contain an entry at prev_log_idx whose term matches prev_log_term
        # print(f"{request.prev_log_term, request.prev_log_idx, len(self.raft_logs)}")

        # if len(self.raft_logs) < request.prev_log_idx or self.raft_logs[request.prev_log_idx - 1].term != request.prev_log_term:
        if len(self.raft_logs) <= request.prev_log_idx or self.raft_logs[request.prev_log_idx].term != request.prev_log_term:
            print(f"Received AppendEntries from {request.leader_id}: Sent False, log doesn't contain an entry at prev_log_idx whose term matches prev_log_term")
            logger.info(f"Node {ID} rejected AppendEntries RPC from {self.leader_id}")
            response.term = self.current_term
            response.success = False
            return response
        
        # refresh heartbeat timer
        self.curr_timeout = time()

        # if an existing entry conflicts with a new one (same index but different terms)
        # if len(self.raft_logs) > request.prev_log_idx and self.raft_logs[request.prev_log_idx - 1].term != request.entries[0].term:
        self.raft_logs = self.raft_logs[:request.prev_log_idx + 1]

        # append any new entries not already in the log
        print(request.entries)
        self.raft_logs.extend(request.entries)
        for log in request.entries:
            self.db.handle_incoming_log(log)
            logger.info(f"Node {ID} (follower) committed the entry {raft_pb2.Log.action.Name(log.cmd)} {log.key} {log.value if log.cmd == raft_pb2.Log.SET else ''} to the state machine.")

        # if leader_commit > commit_index, set commit_index = min(leader_commit, index of last new entry)
        if request.leader_commit_idx > self.commit_index:
            self.commit_index = min(request.leader_commit_idx, len(self.raft_logs) - 1)

        print(f"Received AppendEntries from {request.leader_id}: Sent True")
        logger.info(f"Node {ID} accepted AppendEntries RPC from {self.leader_id}")
        self.current_term = request.term
        self.voted_for = request.leader_id
        response.term = self.current_term
        response.success = True
        self.leader_id = request.leader_id
        if (request.leader_lease.leader_id != -1):
            self.leader_lease.CopyFrom(request.leader_lease)
        self.db.metadata["current_term"] = self.current_term
        self.db.metadata["commit_index"] = self.commit_index
        self.db.metadata["voted_for"] = self.voted_for
        self.db.dump_meta()
        print(f"AppendEntries: responded at time {time()}")
        return response


    def RequestData(self, request, context):
        print(f"RequestData: Received RequestData from {context.peer()} at {time()}")
        logger.info(f"Node {self.leader_id} (leader) received an {raft_pb2.Log.action.Name(request.data.cmd)} {request.data.key} {request.data.value if request.data.cmd == raft_pb2.Log.SET else ''} request")
        response = raft_pb2.DataResponse()
        if self.leader_id == None:
            print(f"RequestData: Leader is None: False")
            response.leader_id = -1
            return response

        response.leader_id = self.leader_id
        if self.leader_lease.leader_id == ID and (time() - self.leader_lease.time) < LEASE_TIMEOUT:
            if request.data.cmd == raft_pb2.Log.GET:
                response.status = True
                response.data.key = request.data.key
                response.data.value = self.db.get(request.data.key)
            elif request.data.cmd == raft_pb2.Log.SET:
                if self.leader_lease.leader_id != ID:
                    print(f"RequestData: Leader does not have lease: False")
                    response.status = False
                    print(self.leader_lease)
                    return response

                log = raft_pb2.Log()
                log.cmd = raft_pb2.Log.SET
                log.key = request.data.key
                log.value = request.data.value
                log.term = self.current_term
                with self.replication_lock:
                    self.raft_logs.append(log)


                nodes_recieved = self.log_replication()
                
                if nodes_recieved > len(NODES) // 2:
                    response.status = True
                    response.leader_id = self.leader_id
                else:
                    response.status = False
                    response.leader_id = self.leader_id

                return response

        else:
            response.status = False
            response.leader_id = self.leader_id
            return response

        return response


if __name__ == "__main__":
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    raft_servicer = RaftServicer()
    raft_pb2_grpc.add_RaftServicer_to_server(raft_servicer, server)
    server.add_insecure_port(f"[::]:{RAFT_PORT}")
    try:
        server.start()
        print(f"Server started at time {time()}")
        sleep(5) # wait for remote servers to start

        for node in NODES:
            channel = grpc.insecure_channel(f"{node}:{RAFT_PORT}")
            stub = raft_pb2_grpc.RaftStub(channel)
            stubs[node] = stub
        raft_servicer.run()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)

