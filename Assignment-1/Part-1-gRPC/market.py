import argparse
import logging

import grpc
from concurrent import futures

import market_pb2
import market_pb2_grpc

from statistics import mean
from urllib.parse import unquote

class MarketServicer(market_pb2_grpc.MarketServicer):
    items: dict[int, market_pb2.Item] = dict()
    sellers: list[str] = list()
    seller_addr: dict[str, int] = dict()
    seller_items: dict[str, list[int]] = dict()
    item_ratings: dict[int, dict[str, int]] = dict()
    item_wishlists: dict[int, list[str]] = dict()
    item_ids: list[int] = list(range(1000, 0, -1))

    def getPeerIP(self, grpc_ctx_peer: str) -> str:
        ctx_peer = unquote(grpc_ctx_peer)
        return ":".join(ctx_peer.split(":")[1:-1])

    # Seller functionality
    def Register(self, request, context):
        logging.info(f"Join request from {unquote(context.peer())}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.seller_uuid not in self.sellers:
            self.sellers.append(request.seller_uuid)
            self.seller_items[request.seller_uuid] = list()
            self.seller_addr[unquote(context.peer())] = request.notif_server_port
            response.status = market_pb2.Response.Status.SUCCESS
        else:
            response.info = "Seller already registered."
        return response
    
    def Sell(self, request, context):
        logging.info(f"Sell request from {unquote(context.peer())}\n{request}")
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
        item.seller_address = unquote(context.peer())
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
        self.item_ratings[item.id] = dict()
        self.seller_items[request.seller_uuid].append(item.id)
        self.item_wishlists[item.id] = list()
        response.status = market_pb2.Response.Status.SUCCESS
        return response

    def Update(self, request, context):
        logging.info(f"Update request from {unquote(context.peer())}\n{request}")
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
        if self.items[request.item_id].seller_address != unquote(context.peer()):
            response.info = "Item not listed by seller."
            return response
        self.items[request.item_id].price = request.item_price
        self.items[request.item_id].quantity = request.item_quantity
        for peer in self.item_wishlists[request.item_id]:
            channel = grpc.insecure_channel(peer)
            stub = market_pb2_grpc.NotificationStub(channel)
            stub.Notify(market_pb2.NotifyRequest(item=self.items[request.item_id]))
        response.status = market_pb2.Response.Status.SUCCESS
        return response

    def Delete(self, request, context):
        logging.info(f"Delete request from {unquote(context.peer())}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.seller_uuid not in self.sellers:
            response.info = "Seller not registered."
            return response
        if request.item_id not in self.items.keys():
            response.info = "Item ID invalid."
            return response
        if self.items[request.item_id].seller_address != unquote(context.peer()):
            response.info = "Item not listed by seller."
            return response
        self.items.pop(request.item_id)
        self.seller_items[request.seller_uuid].remove(request.item_id)
        self.item_wishlists.pop(request.item_id)
        response.status = market_pb2.Response.Status.SUCCESS
        return response

    def Display(self, request, context):
        logging.info(f"Display request from {unquote(context.peer())}\n{request}")
        if request.seller_uuid not in self.sellers:
            return []
        for item_id in self.seller_items[request.seller_uuid]:
            yield self.items[item_id]

    # Buyer functionality
    def Search(self, request, context):
        logging.info(f"Search request from {unquote(context.peer())}\n{request}")
        def filter(item):
            if request.item_name != "":
                if request.item_name.lower() not in item.name.lower():
                    return False
            if request.item_category.upper() not in "ANY":
                for category in market_pb2.ItemCategory.keys():
                    if request.item_category.upper() in category:
                        return True
                return False
            return True
        for item in self.items.values():
            if filter(item):
                yield item

    def Buy(self, request, context):
        logging.info(f"Buy request from {unquote(context.peer())}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.item_id not in self.items.keys():
            response.info = "Item ID invalid."
            return response
        if request.item_quantity > self.items[request.item_id].quantity:
            response.info = "Item quantity unavailable."
            return response
        self.items[request.item_id].quantity -= request.item_quantity
        # Notify seller
        item = self.items[request.item_id]
        peer = self.getPeerIP(item.seller_address) + ':' + str(self.seller_addr[item.seller_address])
        channel = grpc.insecure_channel(peer)
        stub = market_pb2_grpc.NotificationStub(channel)
        stub.Notify(market_pb2.NotifyRequest(item=item))
        response.status = market_pb2.Response.Status.SUCCESS
        return response

    def Wishlist(self, request, context):
        logging.info(f"Wishlist request from {unquote(context.peer())}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.item_id not in self.items.keys():
            response.info = "Item ID invalid."
            return response
        peer = self.getPeerIP(context.peer()) + ':' + str(request.notif_server_port)
        self.item_wishlists[request.item_id].append(peer)
        response.status = market_pb2.Response.Status.SUCCESS
        return response

    def Rate(self, request, context):
        logging.info(f"Rate request from {unquote(context.peer())}\n{request}")
        response = market_pb2.Response()
        response.status = market_pb2.Response.Status.FAILURE
        if request.item_id not in self.items.keys():
            response.info = "Item ID invalid."
            return response
        if request.item_rating not in range(1, 5+1):
            response.info = "Item rating value invalid."
            return response
        self.item_ratings[request.item_id][unquote(context.peer())] = request.item_rating
        self.items[request.item_id].rating = mean(self.item_ratings[request.item_id].values())
        response.status = market_pb2.Response.Status.SUCCESS
        return response


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
