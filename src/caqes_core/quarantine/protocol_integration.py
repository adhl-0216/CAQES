from abc import ABC, abstractmethod
from typing import Optional

class ProtocolIntegration(ABC):
    """Abstract base class for protocol-level quarantine modules."""

    @abstractmethod
    def ban(self, ip_address: str, reason: str, expire_at: Optional[str] = None) -> bool:
        pass

    # @abstractmethod
    # def unban(self, identifier: str, identifier_type: str) -> bool:
    #     pass

    # @abstractmethod
    # def get_client_info(self, ip: str) -> Optional[Dict[str, Any]]:
    #     pass

    # @abstractmethod
    # def is_banned(self, identifier: str, identifier_type: str) -> bool:
    #     pass