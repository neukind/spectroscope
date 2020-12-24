import abc
from pydantic import BaseModel
from spectroscope.model.base import Action
from spectroscope.model.update import BaseUpdate
from typing import Any, List, Optional, Type

ENABLED_BY_DEFAULT = ["balance_alert", "status_alert"]


class ConfigOption(BaseModel):
    name: str
    param_type: Type
    description: Optional[str] = None
    default: Optional[Any] = None
    hide: bool = False


class Module(abc.ABC):
    @property
    def consumed_types(self) -> List[Type[BaseModel]]:
        return self._consumed_types

    config_options = []

    @abc.abstractclassmethod
    def register(cls, **kwargs):
        pass

    @abc.abstractmethod
    def consume(self, updates: List[BaseModel]):
        pass


class Plugin(Module):
    @abc.abstractmethod
    def consume(self, updates: List[Action]):
        pass


class Subscriber(Module):
    @abc.abstractmethod
    def consume(self, updates: List[BaseUpdate]):
        pass
