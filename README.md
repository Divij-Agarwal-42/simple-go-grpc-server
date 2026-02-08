# Simple gRPC server (Go server + Python client)

## Prerequisites
- Go (1.21+ recommended)
- Python 3.10+ and `pip`

## 1. Install Python dependencies
From the repo root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Start the Go gRPC server
In terminal 1, from the repo root:

```bash
go run .
```

Server listens on `localhost:50051`.

## 3. Run the Python client
In terminal 2, from the repo root (with your venv active):

Health check:

```bash
python3 client.py health
```

Tensor validation example:

```bash
python3 client.py check --shape "2,2" --values "1,2,3,4"
```
