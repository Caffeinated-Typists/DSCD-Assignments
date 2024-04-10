from concurrent import futures
from itertools import islice
import grpc
import sys
import numpy as np
import pickle

from proto import mapreduce_pb2
from proto import mapreduce_pb2_grpc

POINTS_FILE:str = "Data/Input/points.txt"
CENTRIODS_FILE:str = "Data/centroids.txt"
MAPPERS_ROOT:str = "Data/Mappers"


class MapperServicer(mapreduce_pb2_grpc.MapperServicer):
    def __init__(self):
        self.mapper_id = 0

    def Map(self, request:mapreduce_pb2.MapRequest, context):
        # read the points and centroids file
        points:np.ndarray = None
        centroids:np.ndarray = None
        self.mapper_id = request.id

        with open(POINTS_FILE, "r") as f:
            points = f.readlines()
            lines = islice(points, request.start, request.end)
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

        # dictionary to store the closest centroid for each point
        closest_centroid = {} 

        # calculate the closest centroid for each point
        for point in points:
            distances = np.linalg.norm(centroids - point, axis=1)
            idx = np.argmin(distances)
            if closest_centroid.get(idx) is None:
                closest_centroid[idx] = list()
                
            closest_centroid[idx].append(point)

        keys = list(closest_centroid.keys())
        values = list(closest_centroid.values())

        key_chunks = np.array_split(keys, request.k)
        value_chunks = np.array_split(values, request.reducers)

        # Reconstruct the chunks as dictionaries and store them in files
        for i, (key_chunk, value_chunk) in enumerate(zip(key_chunks, value_chunks)):
            chunk = dict(zip(key_chunk, value_chunk))
            with open(f"{MAPPERS_ROOT}/M{request.id}/partition_{i}.pkl", "wb") as f:
                pickle.dump(chunk, f)


    def GetMap(self, request:mapreduce_pb2.PartitionRequest, context):
        """Return the partition file for the given partition number"""
        response:mapreduce_pb2.PartitionResponse = mapreduce_pb2.PartitionResponse()

        with open(f"{MAPPERS_ROOT}/M{self.mapper_id}/partition_{request.partition}.pkl", "rb") as f:
            data = pickle.load(f)
            response.data = pickle.dumps(data)

        return response


    def Ping(self, request, context):
        response:mapreduce_pb2.Response = mapreduce_pb2.Response()
        response.status = 1

        return response



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 mapper.py <port>")
        sys.exit(1)
    
    port:int = int(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mapreduce_pb2_grpc.add_MapperServicer_to_server(MapperServicer(), server)
    server.add_insecure_port(f"[::]:{port}")
    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)