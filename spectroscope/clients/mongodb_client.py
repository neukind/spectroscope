from motor import motor_asyncio
import pymongo
import asyncio
import spectroscope
from pymongo import UpdateOne
from spectroscope.module import Module, Plugin, Subscriber
from spectroscope.model.queue import AddKeys, DelKeys, ValKeys

from typing import List, Set, Tuple, Type

log = spectroscope.log()


class MongodbClientStreamer:
    """Stream changes from the mongodb instance. Currently watching for deletes and inserts.

    Args:
        modules: Modules and arguments to initialize before streaming messages.
    """

    def __init__(
        self,
        modules: List[Tuple[Type[Module], dict]],
        db_uri: str,
        db_name: str,
        col_name: str,
    ):
        self.pymongo = pymongo.MongoClient(db_uri)[db_name][col_name]
        self.collection = motor_asyncio.AsyncIOMotorClient(db_uri)[db_name][col_name]
        self.queue: asyncio.Queue = None
        self.subscribers = list()
        self.plugins = list()
        for module, config in modules:
            if issubclass(module, Subscriber):
                self.subscribers.append(module.register(**config))
            elif issubclass(module, Plugin):
                self.plugins.append(module.register(**config))
            else:
                raise TypeError

    def setup(self, queue, validators):
        self.queue = queue
        self.pymongo.bulk_write(
            [
                UpdateOne(
                    {"_id": key},
                    {"$setOnInsert": {"_id": key, "status": 0}},
                    upsert=True,
                )
                for key in validators
            ]
        )
        return self._get_keys()

    def _get_keys(self):
        active_validators = []
        unactive_validators = []
        validator_set = self.pymongo.find({})
        for validator in validator_set:
            if validator['status'] ==3:
                active_validators.append(validator['_id'])
            else:
                unactive_validators.append(validator['_id'])
        return unactive_validators, active_validators
    
    async def run(self):
        insert_vals = []
        delete_vals = []
        pipeline = [
            {
                "$match": {
                    "$or": [{"operationType": "insert"}, {"operationType": "delete"}]
                }
            }
        ]
        async with self.collection.watch(pipeline) as stream:
            while stream.alive:
                change = await stream.try_next()
                if change is not None:
                    if change["operationType"] == "insert":
                        insert_vals.append(change["documentKey"]["_id"])
                    elif change["operationType"] == "delete":
                        delete_vals.append(change["documentKey"]["_id"])
                    elif change["operationType"] == "update":
                        pass  # TODO get fullDocument.status and update validator list of both streams
                    continue
                await self._publish(insert_vals, delete_vals)
                await asyncio.sleep(3)

    async def _publish(self, insert_vals, delete_vals):
        if insert_vals:
            log.debug("Detected {} new keys".format(len(insert_vals)))
            asyncio.create_task(
                self.queue.put_nowait(
                    AddKeys(validator_keys=set(map(bytes.fromhex, insert_vals)))
                )
            )
            if delete_vals:
                log.debug(
                    "Detected {} new and {} deleting keys".format(
                        len(insert_vals), len(delete_vals)
                    )
                )
                asyncio.create_task(
                    self.queue.put_nowait(
                        DelKeys(validator_keys=set(map(bytes.fromhex, delete_vals)))
                    )
                )
        if delete_vals:
            log.debug("Detected {} deleting keys".format(len(delete_vals)))
            asyncio.create_task(
                self.queue.put_nowait(
                    DelKeys(validator_keys=set(map(bytes.fromhex, delete_vals)))
                )
            )
