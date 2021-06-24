#!/bin/bash
set -e
#cd "$(dirname "$0")"

# create directory to store compiled output
mkdir -p proto
# creating a directory was messing around the import of the service_pb2 thus I deleted it.
# now the proto python files are created in the working directory, thus the naas_proto is being created automatically

# build necessary Python libraries for gRPC from protobuf definitions
python -m grpc_tools.protoc \
    -Iinclude/spectroscope-proto \
    --python_out=${PWD}/proto \
    --grpc_python_out=${PWD}/proto \
    include/spectroscope-proto/validator/service.proto \
    include/spectroscope-proto/validator/node.proto 