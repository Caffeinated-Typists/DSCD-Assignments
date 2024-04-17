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
BASE_PORT_MAPPER: int = 50100

CENTRIODS_FILE:str = "Data/centroids.txt"
REDUCERS_ROOT:str = "Data/Reducers"

class ReducerServicer(mapreduce_pb2_grpc.ReducerServicer):

    def __init__(self)->None:

        self.num_dims = None
        self.reducer_id = None
        self.partition_idx = None
        self.num_mappers = None
        self.centroid_points = None

    def __assert_dimensions(self, points:np.ndarray)->None:
            
            if self.num_dims is None:
                self.num_dims = points.shape[1]
            else:
                assert self.num_dims == points.shape[1], "All points must have the same number of dimensions"

    def __fetch_points(self)->None:
        # Fetch the points from the mappers and store them in self.centroid_points
        #   - Assert that all the points have the same number of dimensions

        self.centroid_points = dict()

        for mapper_port in range(BASE_PORT_MAPPER, BASE_PORT_MAPPER + self.num_mappers):
            channel = grpc.insecure_channel(f"127.0.0.1:{mapper_port}")
            mapper_stub = mapreduce_pb2_grpc.MapperStub(channel)

            req:mapreduce_pb2.PartitionRequest = mapreduce_pb2.PartitionRequest(idx=self.partition_idx)
            resp:mapreduce_pb2.PartitionResponse = mapper_stub.GetPartition(req)

            res_data = pickle.loads(resp.data)

            for centroid_id in res_data.keys():

                for point in res_data[centroid_id]:
                    self.__assert_dimensions(point)

                if self.centroid_points.get(centroid_id) is None:
                    self.centroid_points[centroid_id] = list()
                self.centroid_points[centroid_id].extend(res_data[centroid_id])

    def __reduce_compute(self)->None:

        centroid_update = dict()
        for centroid_id in self.centroid_points.keys():
            centroid_update[centroid_id] = [np.zeros(self.num_dims), 0]

        # Calculate the new centroid for the partition
        for centroid_id in self.centroid_points.keys():
            for point in self.centroid_points[centroid_id]:
                centroid_update[centroid_id][0] += point
                centroid_update[centroid_id][1] += 1

        self.new_centroids = dict()
        for centroid_id in centroid_update.keys():
            self.new_centroids[centroid_id] = centroid_update[centroid_id][0] / centroid_update[centroid_id][1]

    def __reduce_finish(self)->None:

        # Write the new centroid to a file
        with open(f"{REDUCERS_ROOT}/R{self.reducer_id + 1}.txt", "w") as f:
            for centroid_id in self.new_centroids.keys():
                f.write(f"{centroid_id}: {self.new_centroids[centroid_id]}\n")

        # Notify the master that the reduce computation is done
        master_stub.ReduceDone(mapreduce_pb2.Response(status=True))

    def __reduce_run(self)->None:
        
        self.__fetch_points()
        self.__reduce_compute()
        self.__reduce_finish()

    def Reduce(self, request:mapreduce_pb2.ReduceRequest, context)->mapreduce_pb2.Response:

        self.reducer_id = request.id
        self.partition_idx = request.partition_idx
        self.num_mappers = request.mappers

        # Launch the reduce_compute method in a separate thread
        thread = threading.Thread(target=self.__reduce_run)
        thread.start()

        return mapreduce_pb2.Response(status=True)
    
    def GetCentroid(self, request, context)->mapreduce_pb2.CentroidResult:

        response:mapreduce_pb2.CentroidResult = mapreduce_pb2.CentroidResult()
        response.status = True
        response.data = pickle.dumps(self.new_centroids)
        return response

        
    def Ping(self, request, context)->mapreduce_pb2.Response:
        return mapreduce_pb2.Response(status=True)

    
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

