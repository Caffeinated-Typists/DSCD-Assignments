from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from datetime import datetime
import zmq
import uuid
import sys


class User:
    """User class to handle the user
    ### Parameters
    - username : str = Name of the user (has to be unique)
    """

    def __init__(self, username: str):
        self.username: str = username
        self.context: zmq.Context = zmq.Context()
        self.groupList: dict = dict()
        self.group_name = None

        self.group_management_socket = None
        self.group_message_socket = None

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
        group_name: str = inquirer.select(
            message="Which group do you want to join?",
            choices=[Choice(group, group) for group in self.groupList]
        ).execute()
        

        # create a socket and connected to message server
        self.group_management_socket = self.context.socket(zmq.REQ)
        self.group_management_socket.connect(f"tcp://{self.groupList[group_name][0]}:{self.groupList[group_name][1]}")

        # send the message, i.e. username, and action
        self.group_management_socket.send_multipart([self.username.encode(), self.uuid.encode(), "JOIN".encode()])

        # receive the response
        response = self.group_management_socket.recv_multipart()
        if (response[0].decode() == "SUCCESS"):
            print(f"LOG: {self.username} joined the group {group_name}")

            messaging_port = int.from_bytes(response[1], "big")

            self.group_name = group_name

            self.group_message_socket = self.context.socket(zmq.REQ)
            self.group_message_socket.connect(f"tcp://{self.groupList[group_name][0]}:{messaging_port}")
            
        else:
            raise RuntimeError(response[0].decode())

    def leave_group(self) -> None:
        """
        Leave the group
        """
        # send the message, i.e. username, and action
        self.group_management_socket.send_multipart([self.username.encode(), self.uuid.encode(), "LEAVE".encode()])

        # receive the response
        response = self.group_management_socket.recv_string()
        if (response == "SUCCESS"):
            print(f"LOG: {self.username} left the group {self.group_name}")
            self.group_name = None

            self.group_message_socket.close()
            self.group_management_socket.close()

            self.group_message_socket = None
            self.group_management_socket = None

        else:
            raise RuntimeError(response)

    def send_message(self) -> None:
        """
        Send a message to the group
        """
        message: str = inquirer.text(message="Enter your message").execute()

        # get current time
        current_time = datetime.now().strftime("%d-%m-%y %H:%M:%S")

        # send the message, i.e. username, and action
        self.group_message_socket.send_multipart([self.username.encode(), self.uuid.encode(), "SEND".encode(), current_time.encode() ,message.encode()])

        # receive the response
        response = self.group_message_socket.recv_string()
        if (response == "SUCCESS"):
            print(f"LOG: {self.username} sent the message to the group {self.group_name}")
        
    
    def get_messages(self) -> None:
        """
        Get the messages from the group
        """
        # get time after which the messages are to be fetched, blank for all messages
        time: str = inquirer.text(message="""Enter the time after which the messages are to be fetched (blank for all messages) \nTime format: dd-mm-yy HH:MM:SS""",
                                  validate= self._time_validator
                                  ).execute()

        # send the message, i.e. username, and action
        self.group_message_socket.send_multipart([self.username.encode(), self.uuid.encode(), "GET".encode(), time.encode()])

        # receive the response
        response = self.group_message_socket.recv_multipart()
        if (response[0].decode() == "SUCCESS"):
            print(f"LOG: {self.username} received the messages from the group {self.group_name}")
            print(response[1].decode())
        else:
            raise RuntimeError(response[0].decode())

    def _time_validator(self, result):
        if result == "":
            return True
        try:
            datetime.strptime(result, "%d-%m-%y %H:%M:%S")
            return True
        except:
            return False


if __name__ == "__main__":
    # take in the username as CLI argument
    if len(sys.argv) != 2:
        print("Usage: python user.py <username>")
        sys.exit(1)
    
    user = User(sys.argv[1])

    while True:
        action:callable = inquirer.select(
            message="What do you want to do?",
            choices=[
                Choice(lambda: user.get_list_of_groups(), "Get list of groups"),
                Choice(lambda: user.join_group(), "Join a group"),
                Choice(None, "Exit")
            ]
        ).execute()

        # execute the action
        if action is None:
            break

        action()

        if user.group_name is not None:
            while user.group_name is not None:
                action:callable = inquirer.select(
                    message=f"({user.group_name}) What do you want to do?",
                    choices=[
                        Choice(lambda: user.leave_group(), "Leave group"),
                        Choice(lambda: user.send_message(), "Send a message"),
                        Choice(lambda: user.get_messages(), "Get messages"),
                    ]
                ).execute()

                action()

        print()