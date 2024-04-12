import argparse
import logging
from subprocess import Popen

import grpc
from concurrent import futures

from proto import mapreduce_pb2
from proto import mapreduce_pb2_grpc

BASE_PORT_MAPPER: int = 50100
BASE_PORT_REDUCER: int = 50200

POINTS_FILE: str = "Data/Input/points.txt"

class MasterServicer(mapreduce_pb2_grpc.MasterServicer):
    # <instance id/port> : <intstance proc>
    mapper_proc: dict[int, Popen] = dict() 
    reducer_proc: dict[int, Popen] = dict()
    # <instance id/port> : <intstance proc>
    mapper: dict[int, mapreduce_pb2_grpc.MapperStub] = dict()
    reducer: dict[int, mapreduce_pb2_grpc.ReducerStub] = dict()

    def MapDone(self, request, context):
        return super().MapDone(request, context)

    def ReduceDone(self, request, context):
        return super().ReduceDone(request, context)

    def run(self, args):
        logging.info(f"Starting {args.num_mappers} mapper instances.")
        for mapper_id in range(BASE_PORT_MAPPER, BASE_PORT_MAPPER + args.num_mappers):
            self.mapper_proc[mapper_id] = Popen(["python3", "src/mapper.py", str(mapper_id)])
            channel = grpc.insecure_channel(f"[::]:{mapper_id}")
            self.mapper[mapper_id] = mapreduce_pb2_grpc.MapperStub(channel)

        logging.info(f"Starting {args.num_reducers} recducer instances.")
        for reducer_id in range(BASE_PORT_REDUCER, BASE_PORT_REDUCER + args.num_reducers):
            self.reducer_proc[reducer_id] = Popen(["python3", "src/reducer.py", str(reducer_id)])
            channel = grpc.insecure_channel(f"[::]:{reducer_id}")
            self.reducer[reducer_id] = mapreduce_pb2_grpc.ReducerStub(channel)

        logging.info(f"Reading input data from '{POINTS_FILE}'.")
        with open(POINTS_FILE) as points_file:
            points = points_file.readlines()
            print(f"read {len(points)} points.")

        logging.info(f"Stopping {args.num_mappers} mapper instances.")
        for mapper in self.mapper_proc.values():
            mapper.terminate()
        
        logging.info(f"Stopping {args.num_reducers} reducer instances.")
        for reducer in self.reducer_proc.values():
            reducer.terminate()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, dest="listen_port", default=50000)
    parser.add_argument("-m", type=int, dest="num_mappers", choices=range(1,10), default=1)
    parser.add_argument("-r", type=int, dest="num_reducers", choices=range(1,10), default=1)
    parser.add_argument("-k", type=int, dest="num_centroid", choices=range(1,10), default=1)
    parser.add_argument("-i", type=int, dest="num_iterations", choices=range(1,10), default=1)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    master = MasterServicer()
    mapreduce_pb2_grpc.add_MasterServicer_to_server(master, server)
    server.add_insecure_port(f"[::]:{args.listen_port}")
    try:
        server.start()
        logging.info(f"Master started, listening on port {args.listen_port}.")
        master.run(args)
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received.")
        server.stop(grace=None)
    logging.info("Master stopped.")
