import cmd
import argparse

import grpc

import market_pb2
import market_pb2_grpc

from concurrent import futures

class NotificationServicer(market_pb2_grpc.NotificationServicer):
    def Notify(self, request, context):
        print(f"(Notification) Listed item purchased on market.")
        print(request)
        return market_pb2.Response(status=market_pb2.Response.Status.SUCCESS)

class BuyerShell(cmd.Cmd):
    intro = "Welcome to the Market!     Type help or ? to list commands\n"
    prompt = "(buyer)> "
    stub: market_pb2_grpc.MarketStub
    notif_port: int
    
    def __init__(self, stub: market_pb2_grpc.MarketStub, notif_port: int) -> None:
        super().__init__()
        self.stub = stub
        self.notif_port = notif_port

    def do_search(self, arg):
        "Search for items on the market."
        request = market_pb2.SearchRequest()
        request.item_name = input("item name: ")
        request.item_category = input("item category: ")
        response = stub.Search(request)
        for item in response:
            print(item)

    def do_buy(self, arg):
        "Buy items from the market."
        request = market_pb2.BuyRequest()
        request.item_id = int(input("item id: "))
        request.item_quantity = int(input("item quantity: "))
        response = stub.Buy(request)
        print(response)

    def do_wishlist(self, arg):
        "Wishlist an item on the market"
        request = market_pb2.WishlistRequest()
        request.item_id = int(input("item id: "))
        request.notif_server_port = self.notif_port
        response = stub.Wishlist(request)
        print(response)

    def do_rate(self, arg):
        "Rate an item on the market"
        request = market_pb2.RateRequest()
        request.item_id = int(input("item id: "))
        request.item_rating = int(input("item rating: "))
        request.notif_server_port = self.notif_port
        response = stub.Rate(request)
        print(response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", type=str, dest="server_ip", default="localhost")
    parser.add_argument("-p", type=int, dest="server_port", default=50051)
    parser.add_argument("-l", type=int, dest="listen_port", default=50052)
    args = parser.parse_args()

    notification_servicer = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    market_pb2_grpc.add_NotificationServicer_to_server(NotificationServicer(), notification_servicer)
    notification_servicer.add_insecure_port(f"[::]:{args.listen_port}")
    notification_servicer.start()
    channel = grpc.insecure_channel(f"{args.server_ip}:{args.server_port}")
    stub = market_pb2_grpc.MarketStub(channel)
    try:
        BuyerShell(stub=stub, notif_port=args.listen_port).cmdloop()
    except KeyboardInterrupt:
        notification_servicer.stop(grace=None)
        print("exit")

