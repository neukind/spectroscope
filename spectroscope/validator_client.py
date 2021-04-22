import spectroscope
from ethereumapis.v1alpha1 import validator_pb2, validator_pb2_grpc
from spectroscope.model import ChainTimestamp, ValidatorIdentity
from spectroscope.model.update import (
    ValidatorActivationUpdate,
    ActivationBatch,
)
from spectroscope.module import Module, Plugin, Subscriber
from typing import List, Set, Tuple, Type

log = spectroscope.log()




class ValidatorClientStreamer:
    """Stream WaitForActivation messages from the beacon node validator gRPC endpoint.

    Args:
        stub: gRPC stub interface to the beacon chain. Useful for dependency injection.
        modules: Modules and arguments to initialize before streaming messages.
    """

    def __init__(
        self,
        stub: validator_pb2_grpc.BeaconNodeValidatorStub,
        modules: List[Tuple[Type[Module], dict]],
    ):
        self.stub = stub
        self.validator_set: Set[bytes] = set()

        self.subscribers = list()
        self.plugins = list()
        for module, config in modules:
            if issubclass(module, Subscriber):
                self.subscribers.append(module.register(**config))
            elif issubclass(module, Plugin):
                self.plugins.append(module.register(**config))
            else:
                raise TypeError

    def add_validators(self, validators: Set[bytes]):
        for validator in validators:
            self.validator_set.add(validator)

    def remove_validators(self, validators: Set[bytes]):
        for validator in validators: 
            self.validator_set.remove(validator)

    def _generate_messages(self):
        log.info("Watching for {} future validators".format(len(self.validator_set)))
        return validator_pb2.ValidatorActivationRequest(
            public_keys=self.validator_set,
        )

    def stream_responses(self, stream):
        av: List[bytes] = list()
        for statuses in stream:
            for validator_info in statuses.statuses:
                log.debug("validator_info : {}".format(validator_info))
                log.debug(
                    "Received Deposit update for validator idx {}".format(validator_info.index)
                )
                updates = [
                    ValidatorActivationUpdate(status=validator_info.status.status),
                ]

                responses = list()
                for subscriber in self.subscribers:
                    batch = ActivationBatch(
                        validator=ValidatorIdentity(
                            pubkey=validator_info.public_key, idx=validator_info.index, 
                        ),
                        queue=validator_info.status.activation_epoch,
                        updates=list(
                            filter(lambda x: type(x) in subscriber.consumed_types, updates)
                        ),
                    )
                    responses.extend((subscriber.consume(batch)))
                
                for plugin in self.plugins:
                    plugin.consume(
                        list(filter(lambda x: type(x) in plugin.consumed_types, responses))
                    )
                
                if validator_info.status.status == validator_pb2._VALIDATORSTATUS.values_by_name["ACTIVE"].number:
                    av.append(validator_info.public_key)
                    continue
                
        log.debug("Is this code reachable? outside for loop of stream responses")
        log.debug("retrieved {} activated pks".format(len(av)))
        return av
    def stream(self):
        return self.stream_responses(self.stub.WaitForActivation(self._generate_messages())) 
                

# the current issue is that the WaitForActivation stream will go from DEPOSITED to ACTIVE directly, without going to Pending. 
# Thus, we will need to combine the validator_client and beacon_client for the best user-experience. 
#as soon as the validator_client stream gives us a valid validator idx, we can try switching to the beacon_client