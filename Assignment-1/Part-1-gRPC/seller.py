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
        response = stub.Register(market_pb2.RegisterRequest(seller_uuid=self.uuid, notif_server_port=1))
        print(market_pb2.Response.Status.Name(response.status), response)

    def do_sell(self, arg):
        "Sell a new item on the market."
        response = stub.Sell(market_pb2.SellRequest(seller_uuid=self.uuid, item=market_pb2.Item()))
        print(market_pb2.Response.Status.Name(response.status), response)

    def do_update(self, arg):
        "Update an existing item on the market."
        response = stub.Update(market_pb2.UpdateRequest(seller_uuid=self.uuid, item_id=0, item=market_pb2.Item()))
        print(market_pb2.Response.Status.Name(response.status), response)

    def do_delete(self, arg):
        "Delete an item on the market."
        response = stub.Delete(market_pb2.DeleteRequest(seller_uuid=self.uuid, item_id=0))
        print(market_pb2.Response.Status.Name(response.status), response)

    def do_display(self, arg):
        "Display all the uploaded items."
        response = stub.Display(market_pb2.DisplayRequest(seller_uuid=self.uuid, seller_address="_"))
        print(response)


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
