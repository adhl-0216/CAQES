from caqes_core.settings import WorkerSettings

from caqes_core.mq import Client, ClientType
from caqes_core.mq.mqtt.mqtt_client import MqttClient

class ClientFactory:
    @staticmethod
    def create(client_type: ClientType, worker_settings: WorkerSettings) -> Client:

        match client_type:
            case ClientType.MQTT:
                return MqttClient(worker_settings)
            case _:
                raise ValueError(f"Unknown client type: {client_type}")
