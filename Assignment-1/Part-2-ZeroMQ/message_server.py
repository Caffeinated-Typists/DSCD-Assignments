import asyncio
import zmq.asyncio

context = zmq.asyncio.Context()

serverList = dict()

async def handle_socket():
    socket = context.socket(zmq.REP)  # Change the socket type to REP
    socket.bind("tcp://*:5000")  # Change the address as per your requirement

    while True:
        message_parts = await socket.recv_multipart()
        message = [part.decode() for part in message_parts]

        print(f"LOG: Join Request from {message[0]} ({message[1]}:{message[2]})")

        # check if group name already exists
        if (message[0] in serverList):
            await socket.send_string("FAILURE: Group name already exists")

        # check if ip address port number pair exists
        elif (message[1] in serverList.values()):
            await socket.send_string("FAILURE: IP address and port number already in use by another server")

        # add group to server list
        else:
            serverList[message[0]] = message[1]
            await socket.send_string("SUCCESS")
            print(f"SUCCESS: {message[0]} ({message[1]}) registered successfully")

asyncio.run(handle_socket())