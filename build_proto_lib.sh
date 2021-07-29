#!/bin/bash
set -e

# build necessary Python libraries for gRPC from protobuf definitions
python -m grpc_tools.protoc \
    -Iproto_files/validator \
    --python_out=${PWD} \
    --grpc_python_out=${PWD} \
    proto_files/validator/service.proto \
    proto_files/validator/node.proto 
