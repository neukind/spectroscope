import grpc
import os
import spectroscope
import asyncio
from typing import List

from ethereumapis.v1alpha1 import beacon_chain_pb2_grpc
from ethereumapis.v1alpha1 import validator_pb2_grpc
from pkg_resources import load_entry_point
from spectroscope.clients.beacon_client import BeaconChainStreamer
from spectroscope.clients.validator_client import ValidatorClientStreamer
from spectroscope.clients.spectroscope_client import SpectroscopeServer

from spectroscope.exceptions import Invalid,ValidatorInvalid,ValidatorActivated


class StreamingClient:
    """ Handles all the spectroscope app's features

    Args:
        validatorstream: stream validator info until its activation: activation epoch, its queue, and its status
        beaconstream: stream validator info per epoch: balances, and its status 
    """
    def __init__(self,
        validatorstream: ValidatorClientStreamer,
        beaconstream: BeaconChainStreamer,
        rpcserver: SpectroscopeServer,
        unactive_validators: List[bytes],
        active_validators: List[bytes]=None,
        #the server that will handle user requests, 
    ):
        self.validatorstream = validatorstream
        self.beaconstream = beaconstream
        self.unactive_validators = unactive_validators
        if active_validators is None:
            self.active_validators = []
        if rpcserver is None:
            self.rpcserver = False
        

    def setup(self):
        self.validatorstream.add_validators(set(map(bytes.fromhex, self.unactive_validators)))
        self.beaconstream.add_validators(set(map(bytes.fromhex, self.active_validators)))

    
    async def loop(self):
        while True:
            tasks = [
                asyncio.create_task(i.stream()) for i in [self.validatorstream,self.beaconstream] if i.count_validators() 
                #asyncio.create_task(self.rpcserver.serve())
            ]
            if not tasks:
                return 

            try:
                await asyncio.gather(*tasks)
            except ValidatorActivated as act:
                self.validatorstream.remove_validators(act.get_keys())
                self.beaconstream.add_validators(act.get_keys())
                for t in tasks:
                    t.cancel()
            finally:
                await asyncio.sleep(1)


    def start(self):
        pass
