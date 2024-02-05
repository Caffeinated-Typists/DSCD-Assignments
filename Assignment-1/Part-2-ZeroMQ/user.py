from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import zmq
import uuid

class User:
    """User class to handle the user
    ### Parameters
    - username : str = Name of the user (has to be unique)
    """

    def __init__(self, username: str):
        self.username: str = username
        self.context: zmq.Context = zmq.Context()
        self.groupList: dict = dict()
        self.group_server = None
        self.group_port = None

        # generates the same UUID for the same username
        self.uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, self.username))
        print(f"LOG: {self.username} has UUID: {self.uuid}")

    
    def get_list_of_groups(self, log:bool = True) -> None:
        """
        Returns the list of groups
        """
        # create a socket and connected to message server
        socket:zmq.Socket = self.context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5001")

        # send the message, i.e. username
        socket.send_multipart([self.username.encode()])

        # receive the response
        response = socket.recv_json()

        # close the socket
        socket.close()

        self.groupList = response
        if log:
            print(f"LOG: {self.username} received the list of groups")
            for group in self.groupList:
                print(f"{group} : {self.groupList[group][0]}:{self.groupList[group][1]}")


    def join_group(self) -> None:
        """
        Join a group
        ### Parameters
        - group_name : str = Name of the group
        """
        # display all the servers, and ask the user to select one
        # if not self.groupList:
        #     self.get_list_of_groups(log=False)
        group_name: str = inquirer.select(
            message="Which group do you want to join?",
            choices=[Choice(group, group) for group in self.groupList]
        ).execute()
        

        # create a socket and connected to message server
        socket:zmq.Socket = self.context.socket(zmq.REQ)
        socket.connect(f"tcp://{self.groupList[group_name][0]}:{self.groupList[group_name][1]}")

        # send the message, i.e. username, and action
        socket.send_multipart([self.username.encode(), self.uuid.encode(), "JOIN".encode()])

        # receive the response
        response = socket.recv_multipart()
        try:
            if (response[0].decode() == "SUCCESS"):
                print(f"LOG: {self.username} joined the group {group_name}")
                self.group_server = f"tcp://{self.groupList[group_name][0]}:{response[1].decode()}"
                self.group_port = self.groupList[group_name][1]
            else:
                raise RuntimeError(response[0].decode())
        finally:
            # close the socket
            socket.close()

    def print_group(self):
        print(f"LOG: {self.username} is in group {self.group_port}, server: {self.group_server}")

if __name__ == "__main__":
    user = User("user1")

    while True:
        action:callable = inquirer.select(
            message="What do you want to do?",
            choices=[
                Choice(lambda: user.get_list_of_groups(), "Get list of groups"),
                Choice(lambda: user.join_group(), "Join a group"),
                Choice(lambda: user.print_group(), "Print group"),
                Choice(None, "Exit")
            ]
        ).execute()

        # execute the action
        if action is None:
            break

        action()
        print()