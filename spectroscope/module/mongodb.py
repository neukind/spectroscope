from enum import Enum

from spectroscope.model.update import Action
from spectroscope.model.database import RaiseUpdateKeys
from spectroscope.module import ConfigOption, Plugin
from spectroscope.constants import enums
import spectroscope
from typing import List
from pymongo import MongoClient, UpdateOne,DeleteOne
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
            self._client = MongoClient(uri_endpoint)
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
        log.debug("trying to put these validator keys:{}".format(validator_keys))
        docs = self._create_updates(validator_keys,status)
        return self._collection.bulk_write(docs)

    def _del(self, validator_keys: List[str],status: int):
        docs = self._create_deletions(validator_keys)
        return self._collection.bulk_write(docs)

    def _up(self, validator_keys: List[str], status: int):
        docs = self._create_updates(validator_keys,status)
        return self._collection.bulk_write(docs)

    def _action(self,validator_keys: List[str], status: int, update_type:int, **kwargs):
        if enums.ActionTypes.ADD.value == update_type:
            return self._add(validator_keys,status)
        elif enums.ActionTypes.UP.value == update_type:
            return self._up(validator_keys,status)
        elif enums.ActionTypes.DEL.value == update_type:
            return self._del(validator_keys,status)

    def consume(self,events: List[Action]):
        result = []
        log.debug("arrived here...")
        for event in events:
            result.append(self._handlers[type(event)](**event.update.get_dict()))
        log.debug("this is the result of the request :{}".format(result))
        return result