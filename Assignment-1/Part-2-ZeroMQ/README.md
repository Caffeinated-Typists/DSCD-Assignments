# Part 2: Using ZeroMQ to build a Low-Level Group Messaging Application

- Author: [Anirudh S. Kumar](https://github.com/Anirudh-S-Kumar)

## Steps to run the code

1. Start the message server by running the following command in the terminal:
```bash
python message_server.py
```

2. Start the group server by running the following command in the terminal:
```bash
python group.py <group_name> <ip_address> <port> <server_ip> <server_port>
```

3. Start the client by running the following command in the terminal:
```bash
python user.py <username> <server_ip> <server_port>
```