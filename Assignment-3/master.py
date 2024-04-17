import argparse
import logging
from subprocess import Popen
from time import sleep

from numpy import random

import grpc
from concurrent import futures

import mapreduce_pb2
import mapreduce_pb2_grpc

BASE_PORT_MAPPER: int = 50100
BASE_PORT_REDUCER: int = 50200

POINTS_FILE: str = "Data/Input/points.txt"
CENTRIODS_FILE:str = "Data/centroids.txt"

# custom classes to store data and state for a mapper/reducer
class Mapper:
    port: int # also considered as id
    stub: mapreduce_pb2_grpc.MapperStub
    process: Popen # mapper process obj
    request: mapreduce_pb2.MapRequest
    status: bool

    def __init__(self, port: int) -> None:
        self.port = port
        self.request = mapreduce_pb2.MapRequest()
        logging.info(f"Starting mapper instance {self.port}.")
        self.process = Popen(["python3", "mapper.py", str(self.port)])
        channel = grpc.insecure_channel(f"127.0.0.1:{self.port}")
        self.stub = mapreduce_pb2_grpc.MapperStub(channel)

    def __del__(self) -> None:
        logging.info(f"Stopping mapper instance {self.port}.")
        self.process.terminate()

class Reducer:
    port: int # alson considered as id
    stub: mapreduce_pb2_grpc.ReducerStub
    process: Popen # reducer process obj
    status: bool

    def __init__(self, port: int) -> None:
        self.port = port
        logging.info(f"Starting reducer instance {self.port}.")
        self.process = Popen(["python3", "reducer.py", str(self.port)])
        channel = grpc.insecure_channel(f"127.0.0.1:{self.port}")
        self.stub = mapreduce_pb2_grpc.ReducerStub(channel)

    def __del__(self) -> None:
        logging.info(f"Stopping reducer instance {self.port}.")
        self.process.terminate()

class MasterServicer(mapreduce_pb2_grpc.MasterServicer):
    num_points: int = 0
    num_mappers: int = 0
    num_reducers: int = 0
    num_centroids: int = 0
    num_iterations: int = 0

    mappers: dict[int, Mapper] = dict()
    reducers: dict[int, Reducer] = dict()
    centroids: list[list[float]] = list()

    def __init__(self, args) -> None:
        super().__init__()
        self.num_mappers = args.num_mappers
        self.num_reducers = args.num_reducers
        self.num_centroids = args.num_centroids
        self.num_iterations = args.num_iterations
        
        # Generate initial set of centroids
        rng = random.default_rng()
        self.centroids = [(rng.random(), rng.random()) for _ in range(self.num_centroids)]

        logging.info(f"Reading input data from '{POINTS_FILE}'.")
        with open(POINTS_FILE) as points_file:
            self.num_points = len(points_file.readlines())
            logging.info(f"Read {self.num_points} points.")

        # setup mappers and reducers
        q, r = divmod(self.num_points, args.num_mappers)
        for i in range(self.num_mappers):
            id = BASE_PORT_MAPPER + i
            mapper = Mapper(id)
            mapper.request.id = id
            mapper.request.reducers = self.num_reducers
            mapper.request.start = i * q + min(i, r)
            mapper.request.end = (i + 1) * q + min(i+1, r)
            self.mappers[id] = mapper
        
        for i in range(self.num_reducers):
            id = BASE_PORT_REDUCER + i
            self.reducers[id] = Reducer(id)

    def run(self):
        cur_iteration: int = 0
        
        for mapper in self.mappers.values():
            mapper.status = False
            del mapper.request.centroids
            # mapper.request.centroids.extend(self.centroids)
            try:
                response = mapper.stub.Map(mapper.request)
                print(response)
            except Exception as e:
                print(e)
        
        while True:
            for mapper in self.mappers.values():
                try:
                    response = mapper.stub.Ping(mapreduce_pb2.Empty())
                    print(response)
                except Exception as e:
                    print(e)
            status = [mapper.status for mapper in self.mappers.values()]
            if False not in status:
                break

        while True:
            for reducer in self.reducers.values():
                try:
                    response = reducer.stub.Ping(mapreduce_pb2.Empty())
                    print(response)
                except Exception as e:
                    print(e)
            status = [reducer.status for reducer in self.reducers.values()]
            if False not in status:
                break


    def MapDone(self, request, context):
        logging.info(f"Received MapDone request from {request.peer}.")
        id = int(request.peer.split(":")[-1])
        self.mappers[id].status = True
        return mapreduce_pb2.Response(status=True)

    def ReduceDone(self, request, context):
        logging.info(f"Received ReduceDone request from {request.peer}.")
        id = int(request.peer.split(":")[-1])
        self.reducers[id].status = True
        return mapreduce_pb2.Response(status=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, dest="listen_port", default=50000)
    parser.add_argument("-m", type=int, dest="num_mappers", choices=range(1,10), default=1)
    parser.add_argument("-r", type=int, dest="num_reducers", choices=range(1,10), default=1)
    parser.add_argument("-k", type=int, dest="num_centroids", choices=range(1,10), default=1)
    parser.add_argument("-i", type=int, dest="num_iterations", choices=range(1,10), default=1)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    logging.info(f"Starting master instance {args.listen_port}.")
    master = MasterServicer(args)
    mapreduce_pb2_grpc.add_MasterServicer_to_server(master, server)
    server.add_insecure_port(f"[::]:{args.listen_port}")
    try:
        server.start()
        sleep(2) # wait for mappers and reducers to start
        master.run()
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received.")
        server.stop(grace=None)
    logging.info("Master stopped.")
