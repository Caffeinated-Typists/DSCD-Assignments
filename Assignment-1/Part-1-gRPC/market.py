import argparse
import logging

import grpc
from concurrent import futures

import market_pb2
import market_pb2_grpc

class MarketServicer(market_pb2_grpc.MarketServicer):
    sellers: list[str] = list()
    items: dict[int, market_pb2.Item] = dict()
    item_ids: list[int] = list(range(1000, 0, -1))
    seller_items: dict[str, list[int]] = dict()

    # Seller functionality
    def Register(self, request, context):
        logging.info(f"Join request from {context.peer()}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.seller_uuid not in self.sellers:
            self.sellers.append(request.seller_uuid)
            self.seller_items[request.seller_uuid] = list()
            response.status = market_pb2.Response.Status.SUCCESS
        else:
            response.info = "Seller already registered."
        return response
    
    def Sell(self, request, context):
        logging.info(f"Sell request from {context.peer()}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.seller_uuid not in self.sellers:
            response.info = "Seller not registered."
            return response
        item = market_pb2.Item()
        item.name = request.item_name
        item.description = request.item_description
        item.quantity = request.item_quantity
        item.price = request.item_price
        item.seller_address = context.peer()
        for category in market_pb2.ItemCategory.keys():
            if request.item_category.upper() in category:
                item.category = market_pb2.ItemCategory.Value(category)
                break
        if item.category == market_pb2.ItemCategory.UNSPECIFIED:
            response.info = "Item category invalid."
            return response
        if item.quantity < 0:
            response.info = "Item quantity invalid."
            return response
        if item.price < 0:
            response.info = "Item price invalid."
            return response
        item.id = self.item_ids.pop()
        self.items[item.id] = item
        self.seller_items[request.seller_uuid].append(item.id)
        response.status = market_pb2.Response.Status.SUCCESS
        return response

    def Update(self, request, context):
        logging.info(f"Update request from {context.peer()}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.seller_uuid not in self.sellers:
            response.info = "Seller not registered."
            return response
        if request.item_id not in self.items.keys():
            response.info = "Item ID invalid."
            return response
        if request.item_price < 0:
            response.info = "Item price invalid."
            return response
        if request.item_quantity < 0:
            response.info = "Item quantity invalid."
            return response
        if self.items[request.item_id].seller_address != context.peer():
            response.info = "Item not listed by seller."
            return response
        self.items[request.item_id].price = request.item_price
        self.items[request.item_id].quantity = request.item_quantity
        response.status = market_pb2.Response.Status.SUCCESS
        return response

    def Delete(self, request, context):
        logging.info(f"Delete request from {context.peer()}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.seller_uuid not in self.sellers:
            response.info = "Seller not registered."
            return response
        if request.item_id not in self.items.keys():
            response.info = "Item ID invalid."
            return response
        if self.items[request.item_id].seller_address != context.peer():
            response.info = "Item not listed by seller."
            return response
        self.items.pop(request.item_id)
        self.seller_items[request.seller_uuid].remove(request.item_id)
        response.status = market_pb2.Response.Status.SUCCESS
        return response

    def Display(self, request, context):
        logging.info(f"Display request from {context.peer()}\n{request}")
        if request.seller_uuid not in self.sellers:
            return []
        for item_id in self.seller_items[request.seller_uuid]:
            yield self.items[item_id]

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
