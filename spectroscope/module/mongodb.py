from enum import Enum

from spectroscope.model.update import Action
from spectroscope.model.database import RaiseUpdateKeys
from spectroscope.module import ConfigOption, Plugin
from spectroscope.constants import enums
import spectroscope
from typing import List
from pymongo import MongoClient, UpdateOne,DeleteOne
from pymongo.results import BulkWriteResult
from pymongo.errors import ConnectionFailure
log = spectroscope.log()

import spectroscope
log = spectroscope.log()
class Mongodb(Plugin):
    _consumed_types = [RaiseUpdateKeys]

    config_options = [
        ConfigOption(
            name="uri_endpoint",
            param_type=str,
            description="Endpoint to database server",
        ),
        ConfigOption(
            name="db_name",
            param_type=str,
            description="Name of database",
        ),
        ConfigOption(
            name="col_name",
            param_type=str,
            description="Name of collection",
        )
    ]

    def __init__(self, uri_endpoint: str, db_name: str, col_name: str):
        try:
            self._client = MongoClient(uri_endpoint,replicaset="rs0")
            self._database = self._client[db_name]
            self._collection = self._database[col_name]
        except ConnectionFailure as e:
            log.error("failed to connect to {}. {}".format(self.uri_endpoint, e))
            raise e
        self._handlers = {
            RaiseUpdateKeys: self._action
        }

    @classmethod
    def register(cls, **kwargs):
        return cls(
            uri_endpoint=kwargs["uri_endpoint"],
            db_name=kwargs.get("db_name", "spectroscope"),
            col_name=kwargs.get("col_name", "validators"),
        )

    def _create_updates(self,validator_keys: List[str],status: int):
        request = []
        for key in validator_keys:
            request.append(
                UpdateOne(
                    {"validator_key":key},
                    {"$setOnInsert":{
                        "validator_key":key,
                        "status":status
                        }
                    },
                    upsert=True,
                )
            )
        return request

    def _create_deletions(self,validator_keys: List[str]):
        request = []
        for key in validator_keys:
            request.append(
                DeleteOne(
                    {"validator_key":key}
                )
            )
        return request

    def _add(self, validator_keys: List[str],status: int):
        return self._response(self._collection.bulk_write(self._create_updates(validator_keys,status), ordered=False))

    def _up(self, validator_keys: List[str], status: int):
        return self._response(self._collection.bulk_write(self._create_updates(validator_keys,status), ordered=False))
 
    def _del(self, validator_keys: List[str],status: int):
        return self._collection.bulk_write(self._create_deletions(validator_keys), ordered=False)

    def _get(self, validator_keys: List[str], status: int):
        validators=[]
        if not validator_keys:
            validators = self._collection.find({},{"validator_key":1})
        else:
            validators = self._collection.find({'validator_key':{'$in':validator_keys}},{"validator_key":1})
        log.debug("docs updated : {}".format(len([x['validator_key'] for x in validators])))
        return [x['validator_key'] for x in validators]

    def _action(self,validator_keys: List[str], status: int, update_type:int, **kwargs):
        if enums.RequestTypes.ADD.value == update_type:
            return self._add(validator_keys,status)
        elif enums.RequestTypes.UP.value == update_type:
            return self._up(validator_keys,status)
        elif enums.RequestTypes.DEL.value == update_type:
            return self._del(validator_keys,status)
        elif enums.RequestTypes.GET.value == update_type:
            return self._get(validator_keys,status)

    def _response(self, bulk_response:BulkWriteResult):
        if not bulk_response.acknowledged:
            return []
        return [bulk_response.upserted_count]

    def consume(self,events: List[Action]):
        result = []
        log.debug("arrived here...")
        for event in events:
            result.append(self._handlers[type(event)](**event.update.get_dict()))
        log.debug("this is the result of the request :{}".format(result))
        return result