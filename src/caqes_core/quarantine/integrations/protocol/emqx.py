import requests
from typing import Optional
import logging
from caqes_core.quarantine import ProtocolIntegration, integration_factory


@integration_factory.register("protocol", "emqx")
class EMQXIntegration(ProtocolIntegration):
    """Protocol quarantine module for EMQX MQTT broker."""

    def __init__(self, base_url: str, api_key: str, api_secret: str):
        self.logger = logging.getLogger("caqes.quarantine.emqx")
        self.base_url = base_url.rstrip('/')
        self.auth = (api_key, api_secret)
        self.by = 'caqes'

    def ban(self, ip_address: str, reason: str, expire_at: Optional[str] = None) -> bool:
        self.logger.info("Starting ban operation")
        self.logger.info(f"Ban details - IP: {ip_address}, Reason: {reason}")

        ban_method = 'peerhost'
        ban_object = ip_address

        payload = {"as": ban_method, "who": ban_object,
                   "by": self.by, "reason": reason}
        if expire_at:
            payload["until"] = expire_at

        self.logger.debug(f"Sending ban request with payload: {payload}")
        try:
            response = requests.post(
                f"{self.base_url}/banned", json=payload, auth=self.auth, timeout=5)
            self.logger.debug(
                f"Ban response: {response.status_code} {response.content}")

            if response.status_code == 200:
                self.logger.info(f"Successfully banned by {ban_method}")
                return True
            else:
                self.logger.error(
                    f"Ban operation failed with status code {response.status_code}")
                self.logger.debug(
                    f"Failed ban response content: {response.content}")
                raise Exception("Response NOT OK.")
        except requests.RequestException as e:
            self.logger.error(f"Request exception during ban operation")
            self.logger.debug(f"Request exception details: {str(e)}")
            raise e

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
