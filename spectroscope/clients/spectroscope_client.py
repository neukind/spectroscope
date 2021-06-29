import asyncio
import grpc
from concurrent import futures
import sys, os
from pathlib import Path
print(os.path.dirname(os.path.abspath("app.py")))
print(str(Path(__file__).parent.parent.parent))
print(str(Path(__file__)))
sys.path.append(os.path.dirname(os.path.abspath("app.py")))
#sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "proto_files")))
from proto_files.validator import service_pb2, service_pb2_grpc
import spectroscope
from spectroscope.exceptions import Interrupt, UserInteraction
from spectroscope.service import rpc_responder
from spectroscope.module import Module
from typing import List, Set, Tuple, Type

class SpectroscopeServer:
  def __init__(
    self,
    host: str,
    port: int,
    modules: List[Tuple[Type[Module], dict]],
  ):
    self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_ValidatorServiceServicer_to_server(
        rpc_responder.RPCValidatorServicer(modules),self.server
      )
    self.server.add_insecure_port('{}:{}'.format(host,port))

  async def serve(self):
    await self.server.start()
