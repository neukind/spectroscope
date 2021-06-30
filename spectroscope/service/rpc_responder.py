from spectroscope.model.update import DatabaseBatch, DatabaseUpdate
import spectroscope
from spectroscope.module import Module, Plugin, Subscriber
from spectroscope.constants import enums
from typing import List, Set, Tuple, Type
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
                status = enums.ValidatorStatus.DEPOSITED.value,
                validator_keys= [val.validator_key for val in request.validators.validator]
                )
        ]
        return self._send_requests(updates)
        
    def UpNodes(self, request, context):
        updates = [
            DatabaseUpdate(
                update_type = enums.ActionTypes.UP.value,
                status = request.status,
                validator_keys= [val.validator_key for val in request.validators.validator]
                )
        ]
        return self._send_requests(updates)

    def DelNodes(self, request, context):
        updates = [
            DatabaseUpdate(
                update_type = enums.ActionTypes.DEL.value,
                status = enums.ValidatorStatus.ACTIVE.value,
                validator_keys= [val.validator_key for val in request.validators.validator]
                )
        ]
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
            if batch.updates:
                responses.extend(subscriber.consume(batch))

        api_results = []
        for plugin in self.plugins:
            actions = list(filter(lambda x: type(x) in plugin.consumed_types, responses))
            if actions:
                api_results = plugin.consume(actions)

        return self._return_api(api_results)

    def _return_api(self, api_results):
        upserted_count = 0
        for api_result in api_results:
            if api_result is not None:
                if api_result.acknowledged:
                    upserted_count += api_result.upserted_count
                else:
                    return service_pb2.RequestsResult(status=400, message="failed to upsert at least one key")
        response = service_pb2.RequestsResult(status=200)
        if upserted_count:
            message  = "Upserted {} keys".format(upserted_count)
            response.message = message
        else:
            response.message = "All the keys were already stored"
        return response