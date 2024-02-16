# Part 1: Using gRPC to implement an Online Shopping Platform
- Author: [Prateek Kumar](https://github.com/prateek21081)

## Build `.proto`s
- `python -m grpc_tools.protoc -I. --python_out=. --pyi_out=. --grpc_python_out=. market.proto `

## Test

### Market
```
$ python market.py -h
usage: market.py [-h] [-p LISTEN_PORT]

options:
  -h, --help      show this help message and exit
  -p LISTEN_PORT
```

### Seller
```
$ python seller.py -h
usage: seller.py [-h] [-c SERVER_IP] [-p SERVER_PORT] [-l LISTEN_PORT]

options:
  -h, --help      show this help message and exit
  -c SERVER_IP
  -p SERVER_PORT
  -l LISTEN_PORT
```

### Buyer
```
$ python buyer.py -h
usage: buyer.py [-h] [-c SERVER_IP] [-p SERVER_PORT] [-l LISTEN_PORT]

options:
  -h, --help      show this help message and exit
  -c SERVER_IP
  -p SERVER_PORT
  -l LISTEN_PORT
```
