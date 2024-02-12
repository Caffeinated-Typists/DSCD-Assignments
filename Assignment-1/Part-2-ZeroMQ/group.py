from datetime import datetime
import asyncio
import zmq.asyncio
import zmq
import ipaddress
import traceback
import sys


MESSAGE_SERVER_IP:str = "127.0.0.1"
MESSAGE_SERVER_PORT:int = 5000


class Group:
    """
    Class to handle the group
    ### Parameters
    - group_name : str = Name of the group
    - ip address : str = IP address of the server
    - port : int = Port number of the server
    """
    def __init__(self, group_name: str, ip_address: str, port: int):
        self.group_name:str = group_name
        self.ip_address:str = ip_address
        self.port:int = port
        self.async_context: zmq.asyncio.Context = zmq.asyncio.Context()
        self.members:dict = dict()
        self.messages:list[tuple] = list()
        self.message_port = port + 1

        # check if IP address is valid
        if not self.is_valid_ip():
            raise ValueError("Invalid IP address")
        
        # check if port number is valid
        if not (1024 <= port <= 65535):
            raise ValueError("Invalid port number")
    
    def register_to_server(self) -> str:
        """
        Registers the group to the server
        """
        ctx:zmq.Context = zmq.Context()

        # create a socket
        socket = ctx.socket(zmq.REQ)

        # connect to the server
        socket.connect(f"tcp://{MESSAGE_SERVER_IP}:{MESSAGE_SERVER_PORT}")

        # send the message, i.e. group name, ip address and port number
        socket.send_multipart([self.group_name.encode(), self.ip_address.encode(), str(self.port).encode()])

        # receive the response
        response = socket.recv_string()

        try:
            if response == "SUCCESS":
                print("SUCCESS: Group registered successfully")
            else:
                raise RuntimeError(f"{response}")
        finally:
            # close the socket
            socket.close()
            ctx.term()
    
    async def session_management(self):
        """
        Registers the client to the group
        """
        user_register_socket = self.async_context.socket(zmq.REP)
        user_register_socket.bind(f"tcp://*:{self.port}")

        while True:
            message = await user_register_socket.recv_multipart()

            username = message[0].decode()
            uuid = message[1].decode()
            action = message[2].decode()

            print(f"LOG: {username} ({uuid}) requested to {action}")

            if action == "JOIN":
                self.members[username] = uuid
                await user_register_socket.send_multipart([b"SUCCESS", self.message_port.to_bytes(2, "big")])
                print(f"LOG: Join Request from {username} ({uuid}) accepted")

            elif action == "LEAVE":
                self.members.pop(username)
                await user_register_socket.send_string("SUCCESS")
                print(f"LOG: Leave Request from {username} ({uuid}) accepted")

            else:
                await user_register_socket.send_string("FAILURE: Invalid action")
                print(f"LOG: Invalid action from {username} ({uuid})")

    async def message_management(self):
        """
        Manages the messages
        """
        message_socket = self.async_context.socket(zmq.REP)
        message_socket.bind(f"tcp://*:{self.message_port}")

        while True:
            message = await message_socket.recv_multipart()

            username = message[0].decode()
            uuid = message[1].decode()
            action = message[2].decode()

            print(f"LOG: Request from {username} ({uuid}), action: {action} ")
            
            try:
                if action == "SEND":
                    self.messages.append((username, uuid, message[3].decode(), message[4].decode()))
                    await message_socket.send_string("SUCCESS")
                
                elif action == "GET":
                    
                    after_time = message[3].decode()

                    if after_time == "":
                        await message_socket.send_multipart([b"SUCCESS", b"\n".join([f"[{time}] {username} ({uuid}): {usr_message}".encode() for username, uuid, time, usr_message in self.messages])])
                    else:
                        # find where to start
                        start = 0
                        after_time = datetime.strptime(after_time, "%d-%m-%y %H:%M:%S")
                        for i, message in enumerate(self.messages):
                            msg_date = datetime.strptime(message[2], "%d-%m-%y %H:%M:%S")
                            if msg_date > after_time:
                                start = i
                                break
                        
                        await message_socket.send_multipart([b"SUCCESS", b"\n".join([f"[{time}] {username} ({uuid}): {usr_message}".encode() for username, uuid, time, usr_message in self.messages[start:]])])

                else:
                    await message_socket.send_string("FAILURE : Invalid action")

            except Exception as e:
                print(f"ERROR: {e}")
                traceback.print_exc()


    def is_valid_ip(self) -> bool:
        """
        Function to check if the IP address is valid
        """
        try:
            ipaddress.ip_address(self.ip_address)
            return True
        except ValueError:
            return False
        
    async def run(self):
        """
        Run the group
        """
        await asyncio.gather(self.session_management(), self.message_management())
        

if __name__ == "__main__":
    # take in the group name, group IP address, group port, message server IP, message server port as CLI argument
    if len(sys.argv) != 6:
        print("Usage: python group.py <group_name> <ip_address> <port> <server_ip> <server_port>")
        sys.exit(1)

    MESSAGE_SERVER_IP = sys.argv[4]
    MESSAGE_SERVER_PORT = int(sys.argv[5])
    group = Group(sys.argv[1], sys.argv[2], int(sys.argv[3]))
    group.register_to_server()
    asyncio.run(group.run())            