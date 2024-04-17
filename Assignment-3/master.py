import argparse
import logging
from subprocess import Popen
from time import sleep

import grpc
from concurrent import futures

import mapreduce_pb2
import mapreduce_pb2_grpc

BASE_PORT_MAPPER: int = 50100
BASE_PORT_REDUCER: int = 50200

POINTS_FILE: str = "Data/Input/points.txt"

class MasterServicer(mapreduce_pb2_grpc.MasterServicer):
    num_mappers: int = 1
    num_reducers: int = 1
    # <instance id/port> : <intstance proc>
    mapper_proc: dict[int, Popen] = dict() 
    reducer_proc: dict[int, Popen] = dict()
    # <instance id/port> : <intstance stub>
    mapper: dict[int, mapreduce_pb2_grpc.MapperStub] = dict()
    reducer: dict[int, mapreduce_pb2_grpc.ReducerStub] = dict()

    num_iterations: int = 1
    
    num_centroids: int = 1
    centroids: list[float] = list()

    map_input_splits: list[tuple[int, int]] = list()

    def __init__(self, args) -> None:
        super().__init__()
        self.num_mappers = args.num_mappers
        self.num_reducers = args.num_reducers
        self.num_iterations = args.num_iterations
        self.num_centroids = args.num_centroids

    def start_mappers(self):
        logging.info(f"Starting {self.num_mappers} mapper instances.")
        for mapper_id in range(BASE_PORT_MAPPER, BASE_PORT_MAPPER + self.num_mappers):
            self.mapper_proc[mapper_id] = Popen(["python3", "mapper.py", str(mapper_id)])
            channel = grpc.insecure_channel(f"127.0.0.1:{mapper_id}")
            self.mapper[mapper_id] = mapreduce_pb2_grpc.MapperStub(channel)

    def start_reducers(self):
        logging.info(f"Starting {self.num_reducers} recducer instances.")
        for reducer_id in range(BASE_PORT_REDUCER, BASE_PORT_REDUCER + self.num_reducers):
            self.reducer_proc[reducer_id] = Popen(["python3", "reducer.py", str(reducer_id)])
            channel = grpc.insecure_channel(f"127.0.0.1:{reducer_id}")
            self.reducer[reducer_id] = mapreduce_pb2_grpc.ReducerStub(channel)

    def stop_mappers(self):
        logging.info(f"Stopping {len(self.mapper_proc)} mapper instances.")
        for mapper in self.mapper_proc.values():
            mapper.terminate()

    def stop_reducers(self):
        logging.info(f"Stopping {len(self.reducer_proc)} reducer instances.")
        for reducer in self.reducer_proc.values():
            reducer.terminate()

    def gen_map_input_splits(self):
        logging.info(f"Reading input data from '{POINTS_FILE}'.")
        with open(POINTS_FILE) as points_file:
            points = points_file.readlines()
            print(f"read {len(points)} points.")
            q, r = divmod(len(points), args.num_mappers)
            self.map_input_splits = [(i * q + min(i, r), (i + 1) * q + min(i+1, r)) for i in range(self.num_mappers)]

    def run(self):
        self.start_mappers()
        self.start_reducers()
        sleep(2) # wait for mappers and reducers to start

        self.gen_map_input_splits()

        # start map jobs
        map_request = mapreduce_pb2.MapRequest()
        map_request.reducers = self.num_reducers
        map_request.centroids.extend(self.centroids)
        for i, mapper_id in enumerate(self.mapper.keys()):
            map_request.id = mapper_id
            map_request.start, map_request.end = self.map_input_splits[i]
            map_response = self.mapper[mapper_id].Map(map_request)
            print(map_response)

    def MapDone(self, request, context):
        return super().MapDone(request, context)

    def ReduceDone(self, request, context):
        return super().ReduceDone(request, context)


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
    master = MasterServicer(args)
    mapreduce_pb2_grpc.add_MasterServicer_to_server(master, server)
    server.add_insecure_port(f"[::]:{args.listen_port}")
    try:
        server.start()
        logging.info(f"Master started, listening on port {args.listen_port}.")
        master.run()
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received.")
        server.stop(grace=None)
    master.stop_mappers()
    master.stop_reducers()
    logging.info("Master stopped.")
