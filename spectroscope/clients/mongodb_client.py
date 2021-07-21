from motor import motor_asyncio
import pymongo
import asyncio
import spectroscope
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
        db_uri:str="mongodb://localhost:27017",
        db_name:str="spectroscope",
        col_name:str="validators",
    ):
        self.collection = motor_asyncio.AsyncIOMotorClient(db_uri)[db_name][col_name]
        self.queue:asyncio.Queue = None
        self.subscribers = list()
        self.plugins = list()
        for module, config in modules:
            if issubclass(module, Subscriber):
                self.subscribers.append(module.register(**config))
            elif issubclass(module, Plugin):
                self.plugins.append(module.register(**config))
            else:
                raise TypeError

    def setup(self,queue):
        self.queue = queue
 

    async def run(self):
        insert_vals = []
        delete_vals = []
        pipeline = [{'$match': { '$or': [{'operationType': 'insert'},{'operationType': 'delete'}]}}]
        async with self.collection.watch(pipeline) as stream:
            while stream.alive:
                change = await stream.try_next()
                if change is not None:
                    if change['operationType'] == 'insert':
                        insert_vals.append(change['fullDocument']['validator_key'])
                    elif change['operationType'] == 'delete':
                        delete_vals.append(change['fullDocument']['validator_key'])
                    log.debug("Detected {} new and {} deleting keys".format(len(insert_vals),len(delete_vals)))
                    continue       
                await self._publish(insert_vals,delete_vals)
                await asyncio.sleep(10)


    async def _publish(self, insert_vals, delete_vals):
        if insert_vals:
            asyncio.create_task(self.queue.put_nowait(AddKeys(validator_keys=set(map(bytes.fromhex,insert_vals)))))
            if delete_vals:
                asyncio.create_task(self.queue.put_nowait(DelKeys(validator_keys=set(map(bytes.fromhex,delete_vals)))))
        if delete_vals:
            asyncio.create_task(self.queue.put_nowait(DelKeys(validator_keys=set(map(bytes.fromhex,delete_vals)))))