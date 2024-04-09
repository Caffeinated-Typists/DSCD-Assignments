import subprocess

ip_addresses = ['192.168.0.1', '192.168.0.2', '192.168.0.3']

reachable = [False for _ in ip_addresses]

while True:
    for ip in ip_addresses:
        result = subprocess.run(['ping', '-c', '1', ip], capture_output=True)
        if result.returncode == 0:
            reachable[ip_addresses.index(ip)] = True
        else:
            reachable[ip_addresses.index(ip)] = False
        if all(reachable):
            break

subprocess.run(['python', '/src/raft.py'])