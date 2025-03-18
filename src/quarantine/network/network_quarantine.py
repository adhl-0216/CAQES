from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class NetworkQuarantine(ABC):
    """Abstract base class for network-level quarantine modules."""
    _registry = {}

    @classmethod
    def register(cls, name: str):
        """Decorator to register a quarantine module."""
        def decorator(subclass):
            cls._registry[name] = subclass
            return subclass
        return decorator

    @classmethod
    def create(cls, module_type: str, **kwargs) -> "NetworkQuarantine":
        """Factory method to create a module instance."""
        if module_type not in cls._registry:
            raise ValueError(f"Unknown Network quarantine module: {module_type}")
        return cls._registry[module_type](**kwargs)

    @abstractmethod
    def ban(self, ip_address: str, reason: str, expire_at: Optional[str] = None) -> bool:
        pass

    # @abstractmethod
    # def unban(self, identifier: str, identifier_type: str) -> bool:
    #     pass

    # @abstractmethod
    # def is_banned(self, identifier: str, identifier_type: str) -> bool:
    #     pass