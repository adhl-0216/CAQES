from abc import ABC, abstractmethod
from typing import Optional, Dict, Any

class ProtocolQuarantine(ABC):
    """Abstract base class for protocol-level quarantine modules."""

    @abstractmethod
    def ban(self, identifier: str, identifier_type: str, reason: str, expire_at: Optional[str] = None) -> bool:
        """
        Ban a client from the protocol service.

        Args:
            identifier: The identifier to ban (e.g., IP, Client ID, etc.).
            identifier_type: Type of identifier (e.g., 'ip', 'clientid').
            reason: Reason for the ban.
            expire_at: Optional expiration time (ISO 8601 format, e.g., '2025-03-17T12:00:00Z').

        Returns:
            bool: True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def unban(self, identifier: str, identifier_type: str) -> bool:
        """
        Remove a ban from a client.

        Args:
            identifier: The identifier to unban.
            identifier_type: Type of identifier (e.g., 'ip', 'clientid').

        Returns:
            bool: True if successful, False otherwise.
        """
        pass

    @abstractmethod
    def get_client_info(self, ip: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve client information based on IP (e.g., to map IP to Client ID).

        Args:
            ip: The IP address to query.

        Returns:
            Dict or None: Client details (e.g., {'clientid': 'xyz', 'ip': '192.168.1.2'}) or None if not found.
        """
        pass

    @abstractmethod
    def is_banned(self, identifier: str, identifier_type: str) -> bool:
        """
        Check if a client is currently banned.

        Args:
            identifier: The identifier to check.
            identifier_type: Type of identifier (e.g., 'ip', 'clientid').

        Returns:
            bool: True if banned, False otherwise.
        """
        pass