import spectroscope
from ethereumapis.v1alpha1 import validator_pb2, validator_pb2_grpc
from spectroscope.model import ChainTimestamp, ValidatorIdentity
from spectroscope.model.update import (
    ValidatorActivationUpdate,
    ActivationBatch,
)
from spectroscope.exceptions import Invalid,ValidatorInvalid,ValidatorActivated
from spectroscope.module import Module, Plugin, Subscriber
from typing import List, Set, Tuple, Type
import asyncio

log = spectroscope.log()

#CONSTANTS
UINT64_MAX = 18446744073709551615
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
        self.closest_activation = UINT64_MAX
        for module, config in modules:
            if issubclass(module, Subscriber):
                self.subscribers.append(module.register(**config))
            elif issubclass(module, Plugin):
                self.plugins.append(module.register(**config))
            else:
                raise TypeError


    def count_validators(self):
        return len(self.validator_set)

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
        for validator_info in stream.statuses:
            if (validator_info.index == UINT64_MAX):
                continue
            if validator_info.status.activation_epoch < self.closest_activation:
                self.closest_activation = validator_info.status.activation_epoch
            updates = [
                ValidatorActivationUpdate(status=validator_info.status.status),
            ]
            responses = list()
            for subscriber in self.subscribers:
                batch = ActivationBatch(
                    validator=ValidatorIdentity(
                        pubkey=validator_info.public_key, idx=validator_info.index, 
                    ),
                    activation_epoch=validator_info.status.activation_epoch,
                    updates=list(
                        filter(lambda x: type(x) in subscriber.consumed_types, updates)
                    ),
                )
                if batch.updates:
                    responses.extend((subscriber.consume(batch)))
            
            for plugin in self.plugins:
                actions = list(filter(lambda x: type(x) in plugin.consumed_types, responses))
                if actions:
                    plugin.consume(actions)
            
            if validator_info.status.status == validator_pb2._VALIDATORSTATUS.values_by_name["ACTIVE"].number:
                av.append(validator_info.public_key)
                continue
        return av

    async def stream(self):
        async for activation_response in self.stub.WaitForActivation(self._generate_messages()).__aiter__():
            self.stream_responses(activation_response)

        activated_validators = list()
        for validator_info in activation_response.statuses:
            if validator_pb2._VALIDATORSTATUS.values_by_number[validator_info.status.status].name == "ACTIVE":
                activated_validators.append(validator_info.public_key)
        log.debug("retrieved {} activated pks".format(len(activated_validators)))
        raise ValidatorActivated(activated_validators)
