import spectroscope
from ethereumapis.v1alpha1 import validator_pb2, validator_pb2_grpc
from spectroscope.model import ChainTimestamp, ValidatorIdentity
from spectroscope.model.update import (
    ValidatorActivationUpdate,
    ActivationBatch,
)
from spectroscope.exceptions import Interrupt, UserInteraction
from spectroscope.module import Module, Plugin, Subscriber
from typing import List, Set, Tuple, Type
import asyncio
import grpc
from concurrent import futures


def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  route_guide_pb2_grpc.add_RouteGuideServicer_to_server(
      RouteGuideServicer(), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  server.wait_for_termination()