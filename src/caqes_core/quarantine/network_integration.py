from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class NetworkIntegration(ABC):
    """Abstract base class for network-level quarantine modules."""

    @abstractmethod
    def ban(self, ip_address: str, reason: str, expire_at: Optional[str] = None) -> bool:
        pass

    # @abstractmethod
    # def unban(self, identifier: str, identifier_type: str) -> bool:
    #     pass

    # @abstractmethod
    # def is_banned(self, identifier: str, identifier_type: str) -> bool:
    #     pass