import abc


class AlertSink(abc.ABC):
    def __init__(self):
        pass

    @abc.abstractmethod
    def alert(self, idx: int, pubkey: bytes, event: str, value: str = None):
        pass

    @abc.abstractmethod
    def clear(self, idx: int, pubkey: bytes, event: str):
        pass