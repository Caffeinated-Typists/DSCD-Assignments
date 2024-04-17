from concurrent import futures
from itertools import islice
from os import mkdir
import grpc
import sys
import numpy as np
import pickle
import threading
import logging
from time import sleep

import mapreduce_pb2
import mapreduce_pb2_grpc

POINTS_FILE:str = "Data/Input/points.txt"
CENTRIODS_FILE:str = "Data/centroids.txt"
MAPPERS_ROOT:str = "Data/Mappers"

MASTER_PORT:int = 50000

class MapperServicer(mapreduce_pb2_grpc.MapperServicer):
    def __init__(self):
        self.mapper_id = 0

    def map_compute(self, id, start, end, r):
        # read the points and centroids file
        points:np.ndarray = None
        centroids:np.ndarray = None
        self.mapper_id = id

        with open(POINTS_FILE, "r") as f:
            points = f.readlines()
            lines = islice(points, start, end)
            lines = list(map(lambda x: x.strip(), lines))
            lines = list(map(lambda x: x.split(','), lines))
            lines = list(map(lambda x: list(map(float, x)), lines))
            points = np.array(lines)

        # read the centroids file
        with open(CENTRIODS_FILE, "r") as f:
            centroids = f.readlines()
            centroids = list(map(lambda x: x.strip(), centroids))
            centroids = list(map(lambda x: x.split(','), centroids))
            centroids = list(map(lambda x: list(map(float, x)), centroids))
            centroids = np.array(centroids)

        # array to store the closest centroid for each point
        closest_centroid = [list() for _ in range(len(centroids))]

        # calculate the closest centroid for each point
        for point in points:
            distances = np.linalg.norm(centroids - point, axis=1)
            idx = np.argmin(distances)                
            closest_centroid[idx].append(point)


        # make the directory for the mapper if it does not exist
        try:
            mkdir(f"{MAPPERS_ROOT}/M{self.mapper_id}")
        except FileExistsError:
            pass

        quotient, remainder = divmod(len(centroids), r)
        splits = ([(i * quotient + min(i, remainder), (i + 1) * quotient + min(i + 1, remainder)) for i in range(r)])


        for idx, split in enumerate(splits):
            chunk = dict()
            for i in range(split[0], split[1]):
                chunk[i] = closest_centroid[i]
            with open(f"{MAPPERS_ROOT}/M{self.mapper_id}/partition_{idx}.pkl", "wb") as f:
                pickle.dump(chunk, f)

        # call the MapDone RPC
        master_stub.MapDone(mapreduce_pb2.DoneRequest(id=self.mapper_id))

    def Map(self, request:mapreduce_pb2.MapRequest, context):
        self.mapper_id = request.id
        logging.info(f"Mapper {self.mapper_id} received Map RPC request from master.")
        thread = threading.Thread(target=self.map_compute, args=(request.id, request.start, request.end, request.reducers))
        thread.start()
        return mapreduce_pb2.Response(status=True)
    

    def GetPartition(self, request:mapreduce_pb2.PartitionRequest, context):
        """Return the partition file for the given partition number"""
        logging.info(f"Mapper {self.mapper_id} received GetPartition RPC request.")
        response:mapreduce_pb2.PartitionResponse = mapreduce_pb2.PartitionResponse()

        with open(f"{MAPPERS_ROOT}/M{self.mapper_id}/partition_{request.idx}.pkl", "rb") as f:
            data = pickle.load(f)
            response.data = pickle.dumps(data)

        return response


    def Ping(self, request, context):
        response:mapreduce_pb2.Response = mapreduce_pb2.Response()
        response.status = True
        return response


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mapper.py <port>")
        sys.exit(1)

    logging.basicConfig(level=logging.INFO)
    
    port:int = int(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mapreduce_pb2_grpc.add_MapperServicer_to_server(MapperServicer(), server)
    server.add_insecure_port(f"[::]:{port}")

    channel = grpc.insecure_channel(f"127.0.0.1:{MASTER_PORT}")
    master_stub = mapreduce_pb2_grpc.MasterStub(channel)

    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)
