import grpc
from concurrent import futures
import sys, os

sys.path.append(os.path.dirname(os.path.abspath("app.py")))
from proto_files.validator import service_pb2_grpc
from spectroscope.service.rpc_responder import RPCValidatorServicer
from spectroscope.module import Module
from typing import List, Set, Tuple, Type
import spectroscope

log = spectroscope.log()


class SpectroscopeServer:
    """Handles all the spectroscope app's features
    rpcserver: serves users for validator list management: AddNodes, UpNodes and DelNodes available
    """

    def __init__(
        self,
        host: str,
        port: int,
        modules: List[Tuple[Type[Module], dict]],
    ):
        self.servicer = RPCValidatorServicer(modules)
        self.server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
        service_pb2_grpc.add_ValidatorServiceServicer_to_server(
            self.servicer, self.server
        )
        self.server.add_insecure_port("{}:{}".format(host, port))

    async def serve(self):
        await self.server.start()

    async def stop(self):
        await self.server.stop(grace=None)
