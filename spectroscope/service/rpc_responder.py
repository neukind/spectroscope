from spectroscope.model.update import ValidatorAddUpdate, ValidatorUpUpdate, ValidatorDelUpdate, UpdateDatabase
import spectroscope
from spectroscope.exceptions import Interrupt, UserInteraction
from spectroscope.module import Module, Plugin, Subscriber
from spectroscope.module import db_update
from spectroscope.constants import enums
from typing import List, Set, Tuple, Type
import asyncio
import grpc
from concurrent import futures
from proto_files.validator import service_pb2, service_pb2_grpc

#This servicer will take the module necessary to work: 
# The database plugin used: For now we are using mongodb
# The db_update subscriber that listens to UpdateDatabase Updates.

class RPCValidatorServicer(service_pb2_grpc.ValidatorServiceServicer):
    def __init__(
        self,
        modules: List[Tuple[Type[Module], dict]],
        ):
        self.subscribers = list()
        self.plugins = list()
        for module,config in modules:
            if issubclass(module, Subscriber):
                self.subscribers.append(module.register(**config))
            elif issubclass(module, Plugin):
                self.plugins.append(module.register(**config))
            else:
                raise TypeError
    
    def AddNodesRequest(self,request,context):
        updates = [ValidatorAddUpdate()]
        update_type = enums.ActionTypes.ADD.value
        status = 0
        validators = request.validators
        self._send_requests(updates, update_type, status, validators)
    
    def UpNodesRequest(self, request, context):
        updates = [ValidatorUpUpdate()]
        update_type = enums.ActionTypes.UP.value
        status = request.status
        validators = request.validators
        self._send_requests(updates, update_type, status, validators)

    def DelNodesRequest(self, request, context):
        updates = [ValidatorDelUpdate()]
        update_type = enums.ActionTypes.DEL.value
        status = -1
        validators = request.validators
        self._send_requests(updates, update_type, status, validators)

    def _send_requests(self, updates, update_type, status, validators):
        responses = list()
        for subscriber in self.subscribers:
            batch = UpdateDatabase(
                validator_keys = validators,
                update_type = update_type,
                status = status,
                updates=list(
                    filter(lambda x: type(x) in subscriber.consumed_types, updates)
                ),
            )
            responses.extend(subscriber.consume(batch))

        for plugin in self.plugins:
            plugin.consume(
                list(filter(lambda x: type(x) in plugin.consumed_types, responses))
            )

    
