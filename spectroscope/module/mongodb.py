from enum import Enum
from spectroscope.model.update import Update, Action, RaiseUpdate, DatabaseBatch
from spectroscope.module import ConfigOption, Plugin
from spectroscope.constants import enums
import spectroscope
from typing import List
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
log = spectroscope.log()
import datetime

import spectroscope
log = spectroscope.log()
class Mongodb(Plugin):
    _consumed_types = [RaiseUpdate]

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
            RaiseUpdate: self._action
        }

    @classmethod
    def register(cls, **kwargs):
        return cls(
            uri_endpoint=kwargs["uri_endpoint"],
            db_name=kwargs.get("db_name", "spectroscope"),
            col_name=kwargs.get("col_name", "validators"),
        )

    def _create_docs(self,validator_keys: List[str],status: int):
        docs = []
        for key in validator_keys:
            docs.append(
                {
                    'validator_key':key,
                    'status':status
                }
            )
        return docs
        
    def _add(self, validator_keys: List[str],status: int):
        log.debug("trying to put these validator keys:{}".format(validator_keys))
        docs = self._create_docs(validator_keys,status)
        self._collection.insert_many(docs)

    def _del(self, validator_keys: List[str],status: int):
        self._collection.delete_many({"validator_key":{"$in":validator_keys}})

    def _up(self, validator_keys: List[str], status: int):
        self._collection.update_many(
            {"validator_key":{"$in":validator_keys}},
            {"$set":{"status":status}}
        )

    def _action(self,validator_keys: List[str], status: int, update_type:int, **kwargs):
        if enums.ActionTypes.ADD.value == update_type:
            self._add(validator_keys,status)
        elif enums.ActionTypes.UP.value == update_type:
            self._up(validator_keys,status)
        elif enums.ActionTypes.DEL.value == update_type:
            self._del(validator_keys,status)

    def consume(self,events: List[Action]):
        log.debug("arrived here...")
        for event in events:
            self._handlers[type(event)](**event.update.get_dict())