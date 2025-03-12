from mq.client_types import ClientType
from mq.mq_client import MQClient
from mq.mqtt_client import MqttClient


class ClientFactory:
    @staticmethod
    def create(client_type: ClientType) -> MQClient:

        match client_type:
            case ClientType.MQTT:
                return MqttClient()
            case _:
                raise ValueError(f"Unknown client type: {client_type}")
