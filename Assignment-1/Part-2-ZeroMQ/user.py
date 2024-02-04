import asyncio
import zmq.asyncio
import ipaddress
import uuid

class User:
    """User class to handle the user
    ### Parameters
    - username : str = Name of the user (has to be unique)
    """
    def __init__(self, username: str):
        self.username: str = username
        self.async_context: zmq.asyncio.Context = zmq.asyncio.Context()
        self.groupList = dict()

        # generates the same UUID for the same username
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.username))
        print(f"LOG: {self.username} has UUID: {self.uuid}")

    
    def get_list_of_groups(self) -> dict:
        """
        Returns the list of groups
        """
        # create a context
        ctx:zmq.Context = zmq.Context()

        # create a socket
        socket = ctx.socket(zmq.REQ)

        # connect to the server
        socket.connect("tcp://localhost:5001")

        # send the message, i.e. username
        socket.send_multipart([self.username.encode()])

        # receive the response
        response = socket.recv_json()

        # close the socket
        socket.close()
        ctx.term()

        self.groupList = response
        print(f"LOG: {self.username} received the list of groups")
        for group in self.groupList:
            print(f"{group} : {self.groupList[group][0]}:{self.groupList[group][1]}")


if __name__ == "__main__":
    user = User("user1")
    user.get_list_of_groups()