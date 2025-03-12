from typing import Any
from paho.mqtt.client import MQTTMessage
from .message import Message


class MqttMessage(Message):
    def __init__(self, message: MQTTMessage):
        self._message = message
        self._data = message.payload

    @property
    def data(self) -> bytes:
        return self._data

    async def ack(self) -> None:
        # MQTT QoS 1 or 2 messages are automatically acknowledged
        pass

    async def nak(self) -> None:
        # MQTT doesn't have a built-in reject mechanism
        # Messages are automatically acknowledged
        pass
