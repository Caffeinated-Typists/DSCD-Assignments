import asyncio
import zmq.asyncio

context = zmq.asyncio.Context()


class MessageServer:
    """
    Class to handle the message server
    """
    def __init__(self):
        self.async_context: zmq.asyncio.Context = zmq.asyncio.Context()
        self.serverList = dict()

        print("LOG: Server started")

    async def handle_server(self):
        group_socket = context.socket(zmq.REP) 
        group_socket.bind("tcp://*:5000")

        while True:
            message_parts = await group_socket.recv_multipart()
            message = [part.decode() for part in message_parts]

            print(f"LOG: Join Request from {message[0]} ({message[1]}:{message[2]})")
            ip_port = (message[1], message[2])
            # check if group name already exists
            if (message[0] in self.serverList):
                await group_socket.send_string("FAILURE: Group name already exists")

            # check if ip address port number pair exists
            
            elif (ip_port in self.serverList.values()):
                await group_socket.send_string("FAILURE: IP address and port number already in use by another server")

            # add group to server list
            else:
                self.serverList[message[0]] = ip_port
                await group_socket.send_string("SUCCESS")
                print(f"SUCCESS: {message[0]} ({message[1]}:{message[2]}) registered successfully")

    async def return_server_list(self):
        """
        Returns the server list
        """
        user_socket = context.socket(zmq.REP)
        user_socket.bind("tcp://*:5001")

        while True:
            message_parts = await user_socket.recv_multipart()
            message = [part.decode() for part in message_parts]

            print(f"LOG: Group List Request from {message[0]}")

            # send the server list
            await user_socket.send_json(self.serverList)

    async def start(self):
        await asyncio.gather(self.handle_server(), self.return_server_list())


if __name__ == "__main__":
    server = MessageServer()
    asyncio.run(server.start())
        