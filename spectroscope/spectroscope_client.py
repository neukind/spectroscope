import spectroscope
from spectroscope.exceptions import Interrupt, UserInteraction
from typing import List, Set, Tuple, Type
import asyncio
import grpc
from concurrent import futures
from proto import service_pb2_grpc


def serve():
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  service_pb2_grpc.add_ValidatorServiceServicer_to_server(
      service_pb2_grpc.ValidatorServiceServicer,server
    )
  server.add_insecure_port('[::]:50051')
  server.start()
  server.wait_for_termination()