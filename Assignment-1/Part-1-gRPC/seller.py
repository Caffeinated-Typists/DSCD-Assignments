import cmd
import uuid
import argparse

import grpc

import market_pb2
import market_pb2_grpc

from concurrent import futures

class NotificationServicer(market_pb2_grpc.NotificationServicer):
    def Notify(self, request, context):
        print(f"(Notification) Wishlisted item updated on market.")
        print(request)
        return market_pb2.Response(status=market_pb2.Response.Status.SUCCESS)

class SellerShell(cmd.Cmd):
    intro = "Welcome to the Market!    Type help or ? to list commands\n"
    prompt = "(seller)> "
    stub: market_pb2_grpc.MarketStub
    uuid: str
    notif_port: int

    def __init__(self, stub: market_pb2_grpc.MarketStub, uuid: str, notif_port: int) -> None:
        super().__init__()
        self.stub = stub
        self.uuid = uuid
        self.notif_port = notif_port

    def do_register(self, arg):
        "Resgister seller on the market if not registered already."
        request = market_pb2.RegisterRequest()
        request.seller_uuid = self.uuid
        request.notif_server_port = self.notif_port
        response = stub.Register(request)
        print(response)

    def do_sell(self, arg):
        "Sell a new item on the market."
        request = market_pb2.SellRequest()
        request.seller_uuid = self.uuid
        request.item_name = input("item name: ")
        request.item_description = input("item description: ")
        request.item_category = input("item category: ")
        request.item_price = float(input("item price: "))
        request.item_quantity = int(input("item quantity: "))
        response = stub.Sell(request)
        print(response)

    def do_update(self, arg):
        "Update an existing item on the market."
        request = market_pb2.UpdateRequest()
        request.seller_uuid = self.uuid
        request.item_id = int(input("item id: "))
        request.item_price = float(input("item price new: "))
        request.item_quantity = int(input("item quantity new: "))
        response = stub.Update(request)
        print(response)

    def do_delete(self, arg):
        "Delete an item on the market."
        request = market_pb2.DeleteRequest()
        request.seller_uuid = self.uuid
        request.item_id = int(input("item id: "))
        response = stub.Delete(request)
        print(response)

    def do_display(self, arg):
        "Display all the uploaded items."
        request = market_pb2.DisplayRequest()
        request.seller_uuid = self.uuid
        response = stub.Display(request)
        for item in response:
            print(item)


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
        SellerShell(stub=stub, uuid=str(uuid.uuid4()), notif_port=args.listen_port).cmdloop()
    except KeyboardInterrupt:
        notification_servicer.stop(grace=None)
        print("exit")
