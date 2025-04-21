from abc import ABC, abstractmethod
from typing import AsyncIterator, Callable
from .message import Message

class Client(ABC):
    @abstractmethod
    async def connect(self) -> None:
        pass

    @abstractmethod
    async def close(self) -> None:
        pass

    @abstractmethod
    async def is_connected(self) -> bool:
        pass

    @abstractmethod
    async def subscribe(self, topic: str, callback: Callable) -> AsyncIterator[Message]:
        pass
