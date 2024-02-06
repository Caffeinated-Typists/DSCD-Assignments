import argparse
import logging

import grpc
from concurrent import futures

import market_pb2
import market_pb2_grpc

class MarketServicer(market_pb2_grpc.MarketServicer):
    # Seller functionality
    def Register(self, request, context):
        logging.info(f"Join request from {context.peer()}\n{request}")
        return market_pb2.Response()
    
    def Sell(self, request, context):
        logging.info(f"Sell request from {context.peer()}\n{request}")
        return market_pb2.Response()

    def Update(self, request, context):
        logging.info(f"Update request from {context.peer()}\n{request}")
        return market_pb2.Response()

    def Delete(self, request, context):
        logging.info(f"Delete request from {context.peer()}\n{request}")
        return market_pb2.Response()

    def Display(self, request, context):
        logging.info(f"Display request from {context.peer()}\n{request}")
        return market_pb2.Item()

    # Buyer functionality
    def Search(self, request, context):
        return super().Search(request, context)

    def Buy(self, request, context):
        return super().Buy(request, context)

    def Wishlist(self, request, context):
        return super().Wishlist(request, context)

    def Rate(self, request, context):
        return super().Rate(request, context)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", type=int, dest="listen_port", default=50051)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_MarketServicer_to_server(MarketServicer(), server)
    server.add_insecure_port(f"[::]:{args.listen_port}")
    try:
        server.start()
        logging.info(f"Server started, listening on port {args.listen_port}.")
        server.wait_for_termination()
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt received.")
        server.stop(grace=None)
    logging.info("Server stopped.")
    market_pb2.Item.ParseFromStringq
