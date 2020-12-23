import abc
from spectroscope.model.base import Action
from spectroscope.module import Module
from typing import List, Type


class BasePlugin(Module):
    @abc.abstractmethod
    def consume(self, updates: List[Action]):
        pass
