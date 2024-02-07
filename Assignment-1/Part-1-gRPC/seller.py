import cmd
import uuid
import argparse

import grpc

import market_pb2
import market_pb2_grpc

class SellerShell(cmd.Cmd):
    intro = "Welcome to the Market!    Type help or ? to list commands\n"
    prompt = "(seller)> "
    stub: market_pb2_grpc.MarketStub
    uuid: str

    def __init__(self, stub: market_pb2_grpc.MarketStub, uuid: str) -> None:
        super().__init__()
        self.stub = stub
        self.uuid = uuid

    def do_register(self, arg):
        "Resgister seller on the market if not registered already."
        request = market_pb2.RegisterRequest()
        request.seller_uuid = self.uuid
        request.notif_server_port = 1
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
    args = parser.parse_args()

    channel = grpc.insecure_channel(f"{args.server_ip}:{args.server_port}")
    stub = market_pb2_grpc.MarketStub(channel)
    try:
        SellerShell(stub, str(uuid.uuid4())).cmdloop()
    except KeyboardInterrupt:
        print("exit")
