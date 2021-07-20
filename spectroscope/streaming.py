from logging import shutdown
from spectroscope.clients.mongodb_client import MongodbClientStreamer
import spectroscope
import asyncio
from typing import List
from spectroscope.clients.beacon_client import BeaconChainStreamer
from spectroscope.clients.validator_client import ValidatorClientStreamer
from spectroscope.service.spectroscope_server import SpectroscopeServer
from spectroscope.exceptions import AddKeys, ValidatorActivated, DelKeys, NoKeys

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
        mongostream: MongodbClientStreamer,
        rpcserver: SpectroscopeServer,
        unactive_validators: List[bytes],
        active_validators: List[bytes]=None,
    ):
        self.validatorstream = validatorstream
        self.beaconstream = beaconstream
        self.mongostream = mongostream
        self.rpcserver = rpcserver
        self.unactive_validators = unactive_validators
        if active_validators is None:
            self.active_validators = []


    
    def setup(self):
        self.validatorstream.add_validators(set(map(bytes.fromhex, self.unactive_validators)))
        self.beaconstream.add_validators(set(map(bytes.fromhex, self.active_validators)))
    
    async def loop(self):
        db_queue = asyncio.Queue()
        while True:
            tasks = [asyncio.create_task(i.stream()) for i in [self.validatorstream,self.beaconstream] if i.count_validators()]
            tasks.append(asyncio.create_task(self.rpcserver.serve()))
            tasks.append(asyncio.create_task(self.mongostream.run(db_queue)))
            log.debug("task list checks part 1: before tasks{}".format(len(tasks)))
            results = await asyncio.gather(*tasks, return_exceptions=True)
            log.debug("checks part 2: after results {}".format(len(results)))
            for result in results:
                log.error(f"Handling error: {result}")
                if isinstance(result, ValidatorActivated):
                    self._update_keys(result)
                    self._prompt_log("{} activated keys".format(len(result.get_keys())))
                elif isinstance(result, AddKeys):
                    self._add_keys(result)
                    self._prompt_log("Added {} keys".format(len(result.get_keys())))
                elif isinstance(result, DelKeys):
                    self._delete_keys(result)
                    self._prompt_log("Deleted {} keys".format(len(result.get_keys())))
                # elif isinstance(result, NoKeys):
                #     tasks.append(asyncio.create_task(self.mongostream.run(db_queue)))
                #     continue
                elif isinstance(result, Exception):
                    log.error(f"Handling general error: {result}")
                elif isinstance(result, type(None)):
                    continue
                await self.shutdown(tasks)

#TODO create the graceful shutdown into restart to remove the runtime error for coroutines not awaited
    async def shutdown(self,tasks):
        log.info("Ending spectroscope, bye bye..")
        for t in tasks:
            t.cancel()
    
    #super hacky way to retrieve the whole list from the database 
    def _retrieve_keys(self):
        validators = self.rpcserver._retrieve_servicer().get_validators()
        return [key.validator_key.decode() for key in validators.validator]
    #back-up method that will reset the whole validator list
    def _rollback_keys(self):
        self.validatorstream.add_validators(self._retrieve_keys)

    def _update_keys(self,result):
        log.debug("updating the list with those keys: {}".format(result.get_keys()))
        self.validatorstream.remove_validators(result.get_keys())
        self.beaconstream.add_validators(result.get_keys())

    def _delete_keys(self, result):
        log.debug("deleting those keys: {}".format(result.get_keys()))
        self.validatorstream.remove_validators(result.get_keys())
        self.beaconstream.remove_validators(result.get_keys())

    def _add_keys(self, result):
        log.debug("adding those keys: {}".format(result.get_keys()))
        self.validatorstream.add_validators(result.get_keys())

    def _prompt_log(self,message):
        log.info("monitoring list modified: {}".format(message))