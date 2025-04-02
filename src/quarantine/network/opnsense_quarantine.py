from typing import Optional
import requests
from datetime import datetime
from quarantine.network.network_quarantine import NetworkQuarantine
import logging

@NetworkQuarantine.register("opnsense")
class OPNSenseQuarantine(NetworkQuarantine):
    """OPNSense Quarantine Module"""

    def __init__(self, base_url: str, api_key: str, api_secret: str):
        """Initialize the OPNSense quarantine module with API credentials."""
        self.logger = logging.getLogger("caqes.quarantine.opnsense")
        self.base_url = base_url.rstrip('/')  # Ensure no trailing slash
        self.auth = (api_key, api_secret)
        self.headers = {"Content-Type": "application/json"}
        self.timeout = 5  # Timeout for requests in seconds
        self.alias_name = "quarantine_iot"  # Define alias name as a class attribute

    def _get_mac_from_ip(self, ip_address: str) -> str:
        """Fetch MAC address for a given IP using ARP or DHCP leases."""
        self.logger.debug(f"Attempting to fetch MAC address for IP {ip_address}")
        try:
            # Try ARP table first
            arp_url = f"{self.base_url}/api/diagnostics/interface/getArp"
            arp_response = requests.get(arp_url, auth=self.auth, headers=self.headers, timeout=self.timeout)
            arp_response.raise_for_status()
            arp_data = arp_response.json()
            
            for entry in arp_data.get('rows', []):
                if entry.get('ip') == ip_address:
                    mac = entry.get('mac')
                    if mac:
                        return mac
                    raise ValueError(f"No valid MAC address found for IP {ip_address} in ARP")
            
            # Fallback to DHCP leases
            dhcp_url = f"{self.base_url}/api/dhcpv4/leases/searchLease"
            dhcp_response = requests.get(dhcp_url, auth=self.auth, headers=self.headers, timeout=self.timeout)
            dhcp_response.raise_for_status()
            dhcp_data = dhcp_response.json()
            
            for lease in dhcp_data.get('rows', []):
                if lease.get('address') == ip_address:
                    mac = lease.get('mac')
                    if mac:
                        return mac
                    raise ValueError(f"No valid MAC address found for IP {ip_address} in DHCP")
            
            raise ValueError(f"No MAC address found for IP {ip_address}")
        
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to fetch MAC address for IP {ip_address}: {str(e)}") from e

    def _alias_exists(self) -> bool:
        """Check if the quarantine_iot alias exists by name."""
        try:
            get_url = f"{self.base_url}/api/firewall/alias/getAliasUUID/?name={self.alias_name}"
            response = requests.get(get_url, auth=self.auth, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return bool(response.json().get('uuid'))  # UUID present means alias exists
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to check alias existence: {str(e)}") from e

    def _create_quarantine_alias(self) -> bool:
        """Create the quarantine_iot alias if it doesn't exist."""
        self.logger.info(f"Creating quarantine alias {self.alias_name}")
        alias_payload = {
            "alias": {
                "enabled": "1",
                "name": self.alias_name,
                "type": "external",  # Use 'external' to allow MAC or IP entries
                "content": "",       # Initially empty
                "description": "Quarantine alias for blocking devices"
            }
        }
        try:
            add_url = f"{self.base_url}/api/firewall/alias/addItem"
            response = requests.post(
                add_url,
                auth=self.auth,
                headers=self.headers,
                json=alias_payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.status_code == 200
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to create alias {self.alias_name}: {str(e)}") from e

    def _add_to_quarantine_alias(self, content: str, description: str) -> bool:
        """Add a MAC or IP address to the quarantine_iot alias, creating it if it doesn't exist."""
        try:
            # Check if alias exists, create it if not
            if not self._alias_exists():
                self.logger.info(f"Alias {self.alias_name} not found, creating it.")
                if not self._create_quarantine_alias():
                    raise RuntimeError(f"Failed to create alias {self.alias_name}")
                self.logger.info(f"Created alias {self.alias_name} successfully.")

            # Add content to the alias
            alias_payload = {
                "alias": {
                    "name": self.alias_name,
                    "content": content,  # MAC or IP to add
                    "description": description
                }
            }
            alias_url = f"{self.base_url}/api/firewall/alias/set"
            response = requests.post(
                alias_url,
                auth=self.auth,
                headers=self.headers,
                json=alias_payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.status_code == 200
        
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to add {content} to quarantine alias: {str(e)}") from e

    def _apply_firewall_changes(self) -> bool:
        """Apply firewall rule changes."""
        self.logger.info("Applying firewall rule changes")
        try:
            apply_url = f"{self.base_url}/api/firewall/filter/apply"
            response = requests.post(
                apply_url,
                auth=self.auth,
                headers=self.headers,
                json={},
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.status_code == 200
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to apply firewall changes: {str(e)}") from e

    def ban(self, ip_address: str, reason: str, expire_at: Optional[str] = None) -> bool:
        """Ban a device by MAC address, falling back to IP if MAC retrieval fails."""
        self.logger.info(f"Attempting to ban device with IP {ip_address}")
        try:
            # Try to ban by MAC address first
            content = self._get_mac_from_ip(ip_address)
            self.logger.info(f"Banning MAC {content} for IP {ip_address}")
            description = f"Quarantined MAC for IP {ip_address}: {reason}"
            
        except (ValueError, RuntimeError) as e:
            self.logger.warning(f"Failed to ban by MAC: {str(e)}. Falling back to IP {ip_address}")
            description = f"Quarantined IP: {reason}"

        finally:
            # Add MAC to quarantine alias
            alias_success = self._add_to_quarantine_alias(content, description)
            if not alias_success:
                raise RuntimeError(f"Failed to update quarantine alias with {content}")

            # Apply firewall changes
            apply_success = self._apply_firewall_changes()
            if not apply_success:
                raise RuntimeError("Failed to apply firewall rule changes")

            return True