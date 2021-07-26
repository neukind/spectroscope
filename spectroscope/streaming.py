from logging import shutdown
from spectroscope.clients.mongodb_client import MongodbClientStreamer
import spectroscope
import asyncio
from typing import List
from spectroscope.clients.beacon_client import BeaconChainStreamer
from spectroscope.clients.validator_client import ValidatorClientStreamer
from spectroscope.service.spectroscope_server import SpectroscopeServer
from spectroscope.exceptions import Interrupt, ValidatorActivated
from spectroscope.model.queue import AddKeys, DelKeys, ActivatedKeys, Publish

log = spectroscope.log()


class StreamingClient:
    """Handles all the spectroscope app's features
    Args:
        validatorstream: stream validator info until its activation: activation epoch, its queue, and its status
        beaconstream: stream validator info per epoch: balances, and its status
        mongostream: stream mongodb changes: Inserts and Deletes
        rpcserver: serves users for validator list management: AddNodes, UpNodes and DelNodes available
    """

    def __init__(
        self,
        validatorstream: ValidatorClientStreamer,
        beaconstream: BeaconChainStreamer,
        mongostream: MongodbClientStreamer,
        rpcserver: SpectroscopeServer,
        unactive_validators: List[str],
        active_validators: List[str] = None,
    ):
        self.validatorstream = validatorstream
        self.beaconstream = beaconstream
        self.mongostream = mongostream
        self.rpcserver = rpcserver
        self.unactive_validators = unactive_validators
        if active_validators is None:
            self.active_validators = []
        self.queue = asyncio.Queue()

    def setup(self):
        self.validatorstream.add_validators(
            set(map(bytes.fromhex, self.unactive_validators))
        )
        self.beaconstream.add_validators(
            set(map(bytes.fromhex, self.active_validators))
        )
        self.mongostream.setup(self.queue, self.unactive_validators)

    async def loop(self):
        while True:
            log.debug("async spectroscope starting..")
            tasks = []
            if self.validatorstream.count_validators():
                tasks.append(
                    asyncio.create_task(
                        self.validatorstream.stream(), name="validator_stream"
                    )
                )
            if self.beaconstream.count_validators():
                tasks.append(
                    asyncio.create_task(
                        self.beaconstream.stream(), name="beacon_stream"
                    )
                )
            tasks.append(asyncio.create_task(self.rpcserver.serve(), name="rpc_server"))
            tasks.append(
                asyncio.create_task(self.mongostream.run(), name="mongo_client")
            )
            tasks.append(
                asyncio.create_task(
                    self.event_consumer(self.queue), name="events_consumer"
                )
            )
            log.debug("running tasks: {}".format([task.get_name() for task in tasks]))
            try:
                await asyncio.gather(*tasks, return_exceptions=False)
            except ValidatorActivated as activated:
                self._update_keys(activated)
            except Exception as inter:
                log.warn(f"got interrupted by: {type(inter)}")
                log.warn(f"details of error: {inter}")
            except KeyError as internal_error:
                log.error("something went wrong here: ")
                log.error(f"KeyError: {internal_error}")
            finally:
                await asyncio.sleep(1)
                await self.shutdown(tasks)

    async def event_consumer(self, queue):
        # while True:
        message = await queue.get()
        if isinstance(message, type(None)):
            log.debug("something went wrong, received None message")
        elif isinstance(message, ValidatorActivated):
            self._update_keys(message)
        elif isinstance(message, AddKeys):
            self._add_keys(message)
        elif isinstance(message, DelKeys):
            self._delete_keys(message)
        else:
            log.debug(f"Unrecognized message type received: {type(message)}")
        # await asyncio.sleep(2)

    # TODO create the graceful shutdown into restart to remove the runtime error for coroutines not awaited
    async def shutdown(self, tasks):
        log.debug("shutting down async spectroscope.. Bye bye")
        for t in tasks:
            t.cancel()

    # super hacky way to retrieve the whole list from the database
    def _retrieve_keys(self):
        validators = self.rpcserver._retrieve_servicer().get_validators()
        return [key.validator_key.decode() for key in validators.validator]

    # back-up method that will reset the whole validator list
    def _rollback_keys(self):
        self.validatorstream.add_validators(self._retrieve_keys)

    def _update_keys(self, result):
        log.debug(
            "updating activated keys: {}".format([x.hex() for x in result.get_keys()])
        )
        self.validatorstream.remove_validators(result.get_keys())
        self.beaconstream.add_validators(result.get_keys())

    def _delete_keys(self, result):
        log.debug("deleting keys: {}".format([x.hex() for x in result.get_keys()]))
        self.validatorstream.remove_validators(result.get_keys())
        self.beaconstream.remove_validators(result.get_keys())

    def _add_keys(self, result):
        log.debug("adding those keys: {}".format([x.hex() for x in result.get_keys()]))
        self.validatorstream.add_validators(result.get_keys())
