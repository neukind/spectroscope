import abc
from pydantic import BaseModel
from typing import List, Type


class Module(abc.ABC):
    @property
    def consumed_types(self) -> List[Type[BaseModel]]:
        return self._consumed_types

    @abc.abstractmethod
    def register(self, **kwargs):
        pass

    @abc.abstractmethod
    def consume(self, updates: List[BaseModel]):
        pass
