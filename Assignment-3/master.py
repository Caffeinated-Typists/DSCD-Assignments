import argparse
import logging
from subprocess import Popen
from time import sleep
from threading import Thread
import pickle

import numpy as np

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
    request: mapreduce_pb2.ReduceRequest
    status: bool

    def __init__(self, port: int) -> None:
        self.port = port
        self.request = mapreduce_pb2.ReduceRequest()
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

    centroids: dict = dict()

    completed: bool = False

    def __init__(self, args) -> None:
        super().__init__()
        self.num_mappers = args.num_mappers
        self.num_reducers = args.num_reducers
        self.num_centroids = args.num_centroids
        self.num_iterations = args.num_iterations
        
        logging.info(f"Reading input data from '{POINTS_FILE}'.")
        dimension = 0
        with open(POINTS_FILE) as points_file:
            points = points_file.readlines()
            self.num_points = len(points)
            dimension = len(points[0].split(','))
        logging.info(f"Read {self.num_points} points.")
        logging.info(f"Point dimension is {dimension}.") 

        # Generate initial set of centroids
        _centroids = np.random.rand(self.num_centroids, dimension)
        for i, c in enumerate(_centroids):
            self.centroids[i] = c
        logging.info(f"Initializing with centroids {self.centroids}")
        with open(CENTRIODS_FILE, 'w') as centroids_file:
            for c in self.centroids.values():
                centroids_file.write(','.join(map(str, list(c)))+'\n')

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
            reducer = Reducer(id)
            reducer.request.id = id
            reducer.request.partition_idx = i
            reducer.request.mappers = self.num_mappers
            self.reducers[id] = reducer
    
    def process_iteration(self, cur_iteration: int):
        logging.info(f"Running iteration {cur_iteration}.")
        for mapper in self.mappers.values():
            mapper.status = False
            try: mapper.stub.Map(mapper.request)
            except Exception as e: print(e)
        
        while True:
            status = [mapper.status for mapper in self.mappers.values()]
            if False not in status: break

        for reducer in self.reducers.values():
            reducer.status = False
            try: reducer.stub.Reduce(reducer.request)
            except Exception as e: print(e)

        while True:
            status = [reducer.status for reducer in self.reducers.values()]
            if False not in status: break

        converged = True
        for reducer in self.reducers.values():
            try:
                response = reducer.stub.GetCentroid(mapreduce_pb2.Empty())
                for i, c in pickle.loads(response.data).items():
                    if np.linalg.norm(self.centroids[i] - c) > 1e-5:
                        converged = False
                    self.centroids[i] = c
            except Exception as e: print(e)
        with open(CENTRIODS_FILE, 'w') as centroids_file:
            for c in self.centroids.values():
                centroids_file.write(','.join(map(str, list(c)))+'\n')
        if converged:
            logging.info(f"Converged on iteration {cur_iteration}.")
            self.completed = True


    def monitor(self):
        def check_recover(instances: list, instance_type: str):
            for instance in instances:
                status = False
                try:
                    response = instance.stub.Ping(mapreduce_pb2.Empty())
                    status = response.status
                except Exception as e:
                    print(f"Caught exception while pinging {instance_type} {instance.port}")
                if status: continue
                logging.info(f"Ping for {instance_type} {instance.port} failed, restarting...")
                instance.process.terminate()
                instance.process = Popen(["python3", f"{instance_type}.py", str(instance.port)])
                sleep(1)
                if instance_type == "mapper":
                    instance.stub.Map(instance.request)
                elif instance_type == "reducer":
                    instance.stub.Reduce(instance.request)

        while self.completed == False:
            check_recover(list(self.mappers.values()), "mapper")
            check_recover(list(self.reducers.values()), "reducer")
        return

    def run(self):
        mon = Thread(target=self.monitor)
        mon.start()
        for cur_iteration in range(0, self.num_iterations):
            self.process_iteration(cur_iteration)
            if self.completed: break
        self.completed = True
        mon.join()

    def MapDone(self, request, context):
        logging.info(f"Received MapDone request from {request.id}.")
        self.mappers[request.id].status = True
        return mapreduce_pb2.Response(status=True)

    def ReduceDone(self, request, context):
        logging.info(f"Received ReduceDone request from {request.id}.")
        self.reducers[request.id].status = True
        return mapreduce_pb2.Response(status=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, dest="listen_port", default=50000)
    parser.add_argument("-m", type=int, dest="num_mappers", choices=range(1,50), default=1)
    parser.add_argument("-r", type=int, dest="num_reducers", choices=range(1,50), default=1)
    parser.add_argument("-k", type=int, dest="num_centroids", choices=range(1,50), default=1)
    parser.add_argument("-i", type=int, dest="num_iterations", choices=range(1,100), default=10)
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
        server.stop(grace=None)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received.")
        server.stop(grace=None)
    logging.info("Master stopped.")
