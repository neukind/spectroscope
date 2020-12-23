import abc
from spectroscope.model.update import BaseUpdate
from spectroscope.module import Module
from typing import List


class Subscriber(Module):
    @abc.abstractmethod
    def consume(self, updates: List[BaseUpdate]):
        pass
