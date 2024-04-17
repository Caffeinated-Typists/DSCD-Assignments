from concurrent import futures
from itertools import islice
from os import mkdir
import grpc
import sys
import numpy as np
import pickle
import threading

import mapreduce_pb2
import mapreduce_pb2_grpc

MASTER_PORT:int = 50000

CENTRIODS_FILE:str = "Data/centroids.txt"

class ReducerServicer(mapreduce_pb2_grpc.ReducerServicer):

    def __init__(self):

        self.reducer_id = None
        self.partition_idx = None
        self.num_mappers = None
        self.centroid_points = None

    def reduce_compute(self):
        
        # Calculate the new centroid for the partition
        #   - handle edge case where all points do not belong to the same centroid
        self.centroid_id = None
        self.accumulated_points = None
        self.point_cnt = None


        # Send the new centroid to the master
        resp:mapreduce_pb2.ReduceResult = mapreduce_pb2.ReduceResult()
        resp.status = True
        resp.centroid_id = self.centroid_id
        resp.updated_point = self.accumulated_points/self.point_cnt
        master_stub.ReduceDone()

        pass

    def Reduce(self, request:mapreduce_pb2.ReduceRequest, context):

        self.reducer_id = request.id
        self.partition_idx = request.partition_idx
        self.num_mappers = request.mappers

        # Fetch the points from the mappers and store them in self.centroid_points

        # Launch the reduce_compute method in a separate thread
        thread = threading.Thread(target=self.reduce_compute)
        thread.start()

        return mapreduce_pb2.Response(status=True)

        
    def Ping(self, request, context):

        response:mapreduce_pb2.Response = mapreduce_pb2.Response()
        response.status = True

        return response
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 reducer.py <port>")
        sys.exit(1)

    port:int = int(sys.argv[1])
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    mapreduce_pb2_grpc.add_ReducerServicer_to_server(ReducerServicer(), server)
    server.add_insecure_port(f"[::]:{port}")

    channel = grpc.insecure_channel(f"127.0.0.1:{MASTER_PORT}")
    master_stub = mapreduce_pb2_grpc.MasterStub(channel)

    try:
        server.start()
        server.wait_for_termination()
    except KeyboardInterrupt:
        server.stop(grace=None)

