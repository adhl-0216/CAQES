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

    def ban(self, ip_address: str, reason: str, expire_at: Optional[str] = None) -> bool:
        try:
            ban_method = 'clientid'
            ban_object = self._get_client_id_by_ip(ip_address)
        except:
            ban_method = 'peerhost'
            ban_object = ip_address

        payload = {"as": ban_method, "who": ban_object, "by": self.by, "reason": reason, "at": datetime.now().isoformat()}

        if expire_at:
            payload["until"] = expire_at
        try:
            response = requests.post(f"{self.base_url}/banned", json=payload, auth=self.auth, timeout=5)
            if response.status_code == 200:
                return True
            else:
                raise Exception(f"Response NOT OK. {response}")
        except requests.RequestException as e:
            raise e
        
    def _get_client_id_by_ip(self, ip_address: str):
        response = requests.get(f"{self.base_url}/clients", auth=self.auth, headers={"Content-Type": "application/json"})
        data = response.json()
        clients = data.get('data', [])
        matching_clients = [client for client in clients if client.get('ip_address')==ip_address]

        if matching_clients:
            return matching_clients[0]['clientid']
        raise Exception("Client Not Found")

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