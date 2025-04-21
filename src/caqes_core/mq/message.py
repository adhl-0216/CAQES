from abc import ABC, abstractmethod

class Message(ABC):
    @property
    @abstractmethod
    def data(self) -> bytes:
        """Return message data"""
        pass

    @abstractmethod
    async def ack(self) -> None:
        """Acknowledge message"""
        pass

    @abstractmethod
    async def nak(self) -> None:
        """Reject/NAK message"""
        pass