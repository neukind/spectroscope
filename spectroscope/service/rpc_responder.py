from spectroscope.model import update
from spectroscope.model.update import DatabaseBatch, DatabaseUpdate
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
# The db_update subscriber that listens to DatabaseBatch Updates.
log = spectroscope.log()
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
    
    def AddNodes(self,request,context):
        updates = [
            DatabaseUpdate(
                update_type = enums.ActionTypes.ADD.value,
                status = 0,
                validator_keys = [val.validator_key for val in request.validators.validator]
            )
        ]
        return self._send_requests(updates)
        
    def UpNodes(self, request, context):
        updates = list(
            DatabaseUpdate(
                update_type = enums.ActionTypes.UP.value,
                status = request.status,
                validator_keys = [val.validator_key for val in request.validators.validator],
            )
        )
        return self._send_requests(updates)

    def DelNodes(self, request, context):
        updates = list(
            DatabaseUpdate(
                update_type = enums.ActionTypes.DEL.value,
                status = -1,
                validator_keys = [val.validator_key for val in request.validators.validator],
            )
        )
        
        return self._send_requests(updates)

    def _send_requests(self, updates):
        log.debug('received these updates {}'.format(updates))
        responses = list()
        for subscriber in self.subscribers:
            batch = DatabaseBatch(
                updates=list(
                    filter(lambda x: type(x) in subscriber.consumed_types, updates)
                ),
            )
            log.debug("subscriber {} has {}".format(subscriber,batch.updates))
            if batch.updates:
                responses.extend(subscriber.consume(batch))
        log.debug("returned values : {}".format(responses))
        for plugin in self.plugins:
            log.debug("plugin {} has".format(plugin))
            debug_filter = list(filter(lambda x: type(x) in plugin.consumed_types, responses))
            log.debug("{}".format(str(debug_filter)))
            plugin.consume(
                list(filter(lambda x: type(x) in plugin.consumed_types, responses))
            )
        response = service_pb2.RequestAccepted(
            status = "Accepted"
        )
        return response

    
