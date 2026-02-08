import argparse
import json
from typing import List

import grpc

import tensor_pb2

def _parse_ints(csv: str) -> List[int]:
    if not csv.strip():
        return []
    return [int(x.strip()) for x in csv.split(",") if x.strip()]

def _parse_floats(csv: str) -> List[float]:
    if not csv.strip():
        return []
    return [float(x.strip()) for x in csv.split(",") if x.strip()]


def call_health(channel: grpc.Channel) -> None:
    health_rpc = channel.unary_unary(
        "/tensor.v1.TensorService/Health",
        request_serializer=tensor_pb2.HealthRequest.SerializeToString,
        response_deserializer=tensor_pb2.HealthResponse.FromString,
    )
    resp = health_rpc(tensor_pb2.HealthRequest())
    print(resp.status)


def call_check_tensor(channel: grpc.Channel, shape: List[int], values: List[float]) -> None:
    check_rpc = channel.unary_unary(
        "/tensor.v1.TensorService/CheckTensor",
        request_serializer=tensor_pb2.CheckTensorRequest.SerializeToString,
        response_deserializer=tensor_pb2.Tensor.FromString,
    )
    req = tensor_pb2.CheckTensorRequest(
        tensor=tensor_pb2.Tensor(shape=shape, values=values),
    )
    resp = check_rpc(req)
    print(
        json.dumps(
            {"shape": list(resp.shape), "values": list(resp.values)},
            indent=2,
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Python gRPC client for TensorService")
    parser.add_argument("--addr", default="localhost:50051", help="gRPC server address")

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("health", help="Call Health endpoint")

    check_parser = subparsers.add_parser("check", help="Call CheckTensor endpoint")
    check_parser.add_argument("--shape", required=True, help='Comma-separated dims, e.g. "2,2"')
    check_parser.add_argument("--values", required=True, help='Comma-separated values, e.g. "1,2,3,4"')

    args = parser.parse_args()

    with grpc.insecure_channel(args.addr) as channel:
        try:
            if args.command == "health":
                call_health(channel)
                return

            shape = _parse_ints(args.shape)
            values = _parse_floats(args.values)
            call_check_tensor(channel, shape, values)
        except grpc.RpcError as err:
            print(f"RPC error: code={err.code().name} message={err.details()}")
            raise SystemExit(1) from err


if __name__ == "__main__":
    main()