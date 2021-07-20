from motor import motor_asyncio
import pymongo
import asyncio
import spectroscope
from spectroscope.module import Module, Plugin, Subscriber
from spectroscope.exceptions import AddDelKeys, AddKeys, DelKeys, NoKeys

from typing import List, Set, Tuple, Type

log = spectroscope.log()
class MongodbClientStreamer:
    """Stream changes from the mongodb instance. Currently watching for deletes and inserts.

    Args:
        modules: Modules and arguments to initialize before streaming messages.
    """

    def __init__(
        self,
        stream,
        modules: List[Tuple[Type[Module], dict]],
        # db_uri:str="mongodb://localhost:27017",
        # db_name:str="spectroscope",
        # col_name:str="validators",
    ):
        #self.collection = motor_asyncio.AsyncIOMotorClient(db_uri)[db_name][col_name]
        self.mongo_stream = stream
        self.subscribers = list()
        self.plugins = list()
        for module, config in modules:
            if issubclass(module, Subscriber):
                self.subscribers.append(module.register(**config))
            elif issubclass(module, Plugin):
                self.plugins.append(module.register(**config))
            else:
                raise TypeError

    async def watcher_while(self,queue):
        insert_vals = []
        delete_vals = []
        pipeline = [{'$match': { '$or': [{'operationType': 'insert'},{'operationType': 'delete'}]}}]
        log.debug("outside while hello?")
        #while self.mongo_stream.alive:
        await asyncio.sleep(10)
        while True:
            log.debug("inside while hello?")
            change = await self.mongo_stream.try_next()
            print("Current resume token: %r" % (self.mongo_stream.resume_token,))
            if change is not None:
                print("change found!")
                if change['operationType'] == 'insert':
                    insert_vals.append(change['fullDocument']['validator_key'])
                #print("Change document: %r" % (change,))
                elif change['operationType'] == 'delete':
                    delete_vals.append(change['fullDocument']['validator_key'])
                log.debug("current list size : {} new and {} deleting keys".format(len(insert_vals),len(delete_vals)))
                continue          
            else:
                print("change not found...")
                await self._raise_interrupt(insert_vals, delete_vals)
                print("this code is never reached right?")
                

    async def watcher(self):
        insert_vals = []
        delete_vals = []
        log.debug("1hello?")

        pipeline = [{'$match': { '$or': [{'operationType': 'insert'},{'operationType': 'delete'}]}}]
        async for insert_change in self.mongo_stream:
            log.debug("hello in for")
            if insert_change['operationType'] == 'insert':
                insert_vals.append(insert_change['fullDocument']['validator_key'])
                # raise AddKeys(insert_vals)
            elif insert_change['operationType'] == 'delete':
                delete_vals.append(insert_change['fullDocument']['validator_key'])
                # raise DelKeys(delete_vals)
            else:
                # raise NoKeys([])
                pass
            await self._raise_interrupt(insert_vals, delete_vals)

    async def _raise_interrupt(self,insert_vals, delete_vals):
        if insert_vals:
            if delete_vals:
                raise AddDelKeys([insert_vals,delete_vals])
            else:
                raise AddKeys(insert_vals)
        elif delete_vals:
            raise DelKeys(delete_vals)
        else:
            raise NoKeys([])

    async def run(self, queue):
        await self.watcher_while(queue)