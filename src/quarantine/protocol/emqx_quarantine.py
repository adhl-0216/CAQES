from datetime import datetime
import requests
from typing import Optional, Dict, Any
from .protocol_quarantine import ProtocolQuarantine

@ProtocolQuarantine.register("emqx")
class EMQXQuarantine(ProtocolQuarantine):
    """Protocol quarantine module for EMQX MQTT broker."""
    def __init__(self, base_url: str, api_key: str, api_secret: str):
        self.base_url = base_url.rstrip('/')
        self.auth = (api_key, api_secret)
        self.by = 'caqes'

    def ban(self, identifier: str, identifier_type: str, reason: str, expire_at: Optional[str] = None) -> bool:
        if identifier_type not in ["peerhost", "clientid"]:
            return False
        payload = {"as": identifier_type, "who": identifier, "by": self.by, "reason": reason, "at": datetime.now().isoformat()}
        if expire_at:
            payload["until"] = expire_at
        try:
            response = requests.post(f"{self.base_url}/banned", json=payload, auth=self.auth, timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    # def unban(self, identifier: str, identifier_type: str) -> bool:
    #     if identifier_type not in ["peerhost", "clientid"]:
    #         return False
    #     try:
    #         response = requests.delete(f"{self.base_url}/banned/{identifier_type}/{identifier}", auth=self.auth, timeout=5)
    #         return response.status_code == 200
    #     except requests.RequestException:
    #         return False

    # def get_client_info(self, ip: str) -> Optional[Dict[str, Any]]:
    #     try:
    #         response = requests.get(f"{self.base_url}/clients?ip_address={ip}", auth=self.auth, timeout=5)
    #         if response.status_code == 200 and response.json()["data"]:
    #             client = response.json()["data"][0]
    #             return {"clientid": client["clientid"], "ip": client["ip_address"], "connected": client["connected"]}
    #         return None
    #     except requests.RequestException:
    #         return None

    # def is_banned(self, identifier: str, identifier_type: str) -> bool:
    #     if identifier_type not in ["peerhost", "clientid"]:
    #         return False
    #     try:
    #         response = requests.get(f"{self.base_url}/blacklist", auth=self.auth, timeout=5)
    #         if response.status_code == 200:
    #             banned = [item for item in response.json()["data"] if item["type"] == identifier_type and item["value"] == identifier]
    #             return bool(banned)
    #         return False
    #     except requests.RequestException:
    #         return False