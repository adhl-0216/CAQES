import asyncio
import logging
from typing import Callable, List
from paho.mqtt.client import Client as MQTTClient, MQTTMessage

from caqes_core.settings.worker_settings import WorkerSettings
from caqes_core.mq.client import Client
from .mqtt_message import MqttMessage


class MqttClient(Client):
    def __init__(self, settings: WorkerSettings):
        self.settings = settings
        self._connect_future: asyncio.Future | None = None
        self.callback: Callable | None = None
        self.loop: asyncio.AbstractEventLoop | None = None
        self.subscriptions : List[str] = []

        # Set up callbacks
        self.client = MQTTClient()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            if self._connect_future and not self._connect_future.done():
                self._connect_future.set_result(True)
        else:
            if self._connect_future and not self._connect_future.done():
                self._connect_future.set_exception(
                    ConnectionError(f"Connection failed with code {rc}")
                )

    def _on_message(self, client, userdata, message: MQTTMessage):
        if self.callback and self.loop:
            asyncio.run_coroutine_threadsafe(
                self.callback(MqttMessage(message)),
                self.loop
            )

    async def connect(self) -> None:
        self.loop = asyncio.get_event_loop()
        last_error = None
        for attempt in range(self.settings.max_retries):
            try:
                # Create a Future to track the connection status
                # This will be resolved in _on_connect callback
                self._connect_future = asyncio.Future()

                # Set up connection - this returns immediately
                self.client.username_pw_set(
                    self.settings.username,
                    self.settings.password
                )
                self.client.connect(
                    self.settings.host,
                    self.settings.port
                )
                self.client.loop_start()

                # Wait for the Future to be resolved by _on_connect
                # This ensures we don't proceed until connection is established
                await asyncio.wait_for(
                    self._connect_future,
                    timeout=self.settings.retry_delay
                )
                return
            except Exception as e:
                last_error = e
                if attempt < self.settings.max_retries - 1:
                    await asyncio.sleep(self.settings.retry_delay * (2 ** attempt))

        raise ConnectionError(
            f"Failed to connect after {self.settings.max_retries} attempts. Last error: {last_error}"
        )

    async def close(self) -> None:
        self.client.loop_stop()
        self.client.disconnect()

    async def is_connected(self) -> bool:
        return self.client.is_connected()

    async def reconnect(self) -> None:
        await self.close()
        await self.connect()
        # Restore subscriptions
        for topic in self.subscriptions:
            self.client.subscribe(topic)

    async def subscribe(self, topic: str, callback: callable) -> None:
        if not await self.is_connected():
            raise RuntimeError("Not connected to MQTT broker")
        try:
            self.client.subscribe(topic)
        except Exception as e:
            raise e
        self.callback = callback
