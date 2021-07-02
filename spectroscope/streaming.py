import grpc
import os
import spectroscope
import asyncio
from typing import List
from spectroscope.clients.beacon_client import BeaconChainStreamer
from spectroscope.clients.validator_client import ValidatorClientStreamer
from spectroscope.service.spectroscope_server import SpectroscopeServer
from proto_files.validator import service_pb2, service_pb2_grpc

from spectroscope.exceptions import NewKeys, ValidatorActivated, NewValidatorList

log = spectroscope.log()

class StreamingClient:
    """ Handles all the spectroscope app's features

    Args:
        validatorstream: stream validator info until its activation: activation epoch, its queue, and its status
        beaconstream: stream validator info per epoch: balances, and its status 
        rpcserver: serves users for validator list management: AddNodes, UpNodes and DelNodes available
    """
    def __init__(self,
        validatorstream: ValidatorClientStreamer,
        beaconstream: BeaconChainStreamer,
        rpcserver: SpectroscopeServer,
        unactive_validators: List[bytes],
        active_validators: List[bytes]=None,
    ):
        self.validatorstream = validatorstream
        self.beaconstream = beaconstream
        self.rpcserver = rpcserver
        self.unactive_validators = unactive_validators
        if active_validators is None:
            self.active_validators = []


    def setup(self):
        self.validatorstream.add_validators(set(map(bytes.fromhex, self.unactive_validators)))
        self.beaconstream.add_validators(set(map(bytes.fromhex, self.active_validators)))

    def _retrieve_keys(self):
        validators = self.rpcserver._retrieve_servicer().get_validators()
        return [key.validator_key.decode() for key in validators.validator]

    def _update_keys(self):
        self.validatorstream.add_validators(set(map(bytes.fromhex, self._retrieve_keys)))

    async def loop(self):
        while True:
            tasks = [asyncio.create_task(i.stream()) for i in [self.validatorstream,self.beaconstream] if i.count_validators()]
            tasks.append(asyncio.create_task(self.rpcserver.serve()))
            try:
                await asyncio.gather(*tasks)
            except ValidatorActivated as act:
                self.validatorstream.remove_validators(act.get_keys())
                self.beaconstream.add_validators(act.get_keys())
            except NewKeys as new_list:
                print("Exception raised!{}".format(new_list))
                validators_set = self.rpcserver.servicer.get_validators()
                self.validatorstream.update_validators(validators_set)
                self.beaconstream.update_validators(validators_set)
            except KeyboardInterrupt:
                await self.rpcserver.stop()
                for t in tasks:
                    t.cancel()
                log.info("shutting down the server.. Goodbye !")
                break
            finally:
                await asyncio.sleep(1)

#TODO create the graceuful shutdown into restart to remove the runtime error for coroutines not awaited
    async def shutdown(self,signal,loop):
        pass
    
    def start(self):
        pass
