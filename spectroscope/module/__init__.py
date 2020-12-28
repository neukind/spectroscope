import abc
from pydantic import BaseModel
from spectroscope.model import Event
from typing import Any, List, Optional, Type

ENABLED_BY_DEFAULT = ["balance_alert", "status_alert"]


class ConfigOption(BaseModel):
    name: str
    param_type: Type
    description: Optional[str] = None
    default: Optional[Any] = None
    hide: bool = False


class Module(abc.ABC):
    _consumed_types: List[Type[Event]]

    @property
    def consumed_types(self) -> List[Type[Event]]:
        return self._consumed_types

    config_options: List[ConfigOption] = []

    @abc.abstractclassmethod
    def register(cls, **kwargs):
        pass

    @abc.abstractmethod
    def consume(self, updates: List[Event]):
        pass


class Plugin(Module):
    @abc.abstractmethod
    def consume(self, updates: List[Event]):
        pass


class Subscriber(Module):
    @abc.abstractmethod
    def consume(self, updates: List[Event]):
        pass
