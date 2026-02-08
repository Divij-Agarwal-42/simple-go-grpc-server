package main

import (
	"context"
	"log"
	"math"
	"net"

	tensorpb "example/hello/pb"
	"google.golang.org/grpc"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
)

const grpcAddr = ":50051"

type tensorServer struct {
	tensorpb.UnimplementedTensorServiceServer
}

func (s *tensorServer) Health(context.Context, *tensorpb.HealthRequest) (*tensorpb.HealthResponse, error) {
	return &tensorpb.HealthResponse{Status: "ok"}, nil
}

func (s *tensorServer) CheckTensor(_ context.Context, req *tensorpb.CheckTensorRequest) (*tensorpb.Tensor, error) {
	if req == nil || req.Tensor == nil {
		return nil, status.Error(codes.InvalidArgument, "tensor is required")
	}

	t := req.Tensor
	if len(t.Shape) == 0 {
		return nil, status.Error(codes.InvalidArgument, "shape is required")
	}

	expectedValues := int64(1)
	for i, dim := range t.Shape {
		if dim <= 0 {
			return nil, status.Errorf(codes.InvalidArgument, "shape[%d] must be > 0", i)
		}
		if expectedValues > math.MaxInt64/dim {
			return nil, status.Error(codes.InvalidArgument, "shape product overflow")
		}
		expectedValues *= dim
	}

	if int64(len(t.Values)) != expectedValues {
		return nil, status.Errorf(codes.InvalidArgument, "invalid tensor: got %d values, expected %d from shape", len(t.Values), expectedValues)
	}

	return t, nil
}

func main() {
	lis, err := net.Listen("tcp", grpcAddr)
	if err != nil {
		log.Fatalf("failed to listen on %s: %v", grpcAddr, err)
	}

	s := grpc.NewServer()
	tensorpb.RegisterTensorServiceServer(s, &tensorServer{})

	log.Printf("gRPC server listening on %s", grpcAddr)
	if err := s.Serve(lis); err != nil {
		log.Fatalf("server stopped with error: %v", err)
	}
}
