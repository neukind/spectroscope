#!/bin/bash

python -m grpc_tools.protoc \
  -I include/ethereumapis \
  -I include/gogo \
  -I include/googleapis \
  --python_out=. \
  include/ethereumapis/eth/v1alpha1/attestation.proto \
  include/ethereumapis/eth/v1alpha1/beacon_block.proto \
  include/ethereumapis/eth/v1alpha1/beacon_chain.proto \
  include/ethereumapis/eth/v1alpha1/validator.proto \
  include/gogo/github.com/gogo/protobuf/gogoproto/gogo.proto \
  include/googleapis/google/api/annotations.proto \
  include/googleapis/google/api/http.proto

python -m grpc_tools.protoc \
  -I include/ethereumapis \
  -I include/gogo \
  -I include/googleapis \
  --grpc_python_out=. \
  include/ethereumapis/eth/v1alpha1/beacon_chain.proto
