from dataclasses import dataclass, field
from googly_eyes.models import FederatedActionMessage
from googly_eyes.transport import MessageTransport, MessageTransportConfig, MessageTransportFeatures

import paho.mqtt.client as mqtt_client

@dataclass
class MQTTTransportConfig(MessageTransportConfig):
    """Configuration for the MQTT transport."""
    broker: str
    port: int = 1883
    publish_topics: list[str] = field(default_factory=list)
    subscribe_topics: list[str] = field(default_factory=list)
    client_id: str = "googly_eyes_client"
    username: str | None = None
    password: str | None = None

class MQTTTransport(MessageTransport):
    """Message transport using MQTT pub/sub protocol."""
    _available_features: MessageTransportFeatures = MessageTransportFeatures.SEND_RECEIVE
    _config: MQTTTransportConfig 

    def __init__(self, config: MQTTTransportConfig) -> None:
        super().__init__(config)
        self._client = mqtt_client.Client(client_id=config.client_id,callback_api_version=mqtt_client.CallbackAPIVersion.VERSION2) # type: ignore

    def on_connect(self, client: mqtt_client.Client, userdata: object, flags: dict[str, int], rc: int) -> None:
        """Callback for when the client connects to the broker."""
        self._logger.info(f"Connected to MQTT broker with result code {rc}")
        for topic in self._config.subscribe_topics:
            client.subscribe(topic)
            self._logger.info(f"Subscribed to topic {topic}")

    def on_message(self, client: mqtt_client.Client, userdata: object, message: mqtt_client.MQTTMessage) -> None:
        """Callback for when a message is received from the broker."""
        self._logger.debug(f"Received message on topic {message.topic}: {message.payload.decode()}")
        # Assuming the payload is a JSON string that can be converted to FederatedActionMessage
        try:
            action_message = FederatedActionMessage.from_json(message.payload.decode())
            self._message_received(action_message)
        except Exception as e:
            self._logger.error(f"Failed to parse message: {e}")

    @property
    def config_type(self) -> type[MQTTTransportConfig]:
        return MQTTTransportConfig

    def _start(self) -> bool:
        self._client.username_pw_set(self._config.username, self._config.password)
        self._client.connect(
            self._config.broker,
            port=self._config.port,
            keepalive=60,
            bind_address=""
        )
        self._client.loop_start()
        return True
    
    def _stop(self) -> None:
        self._client.loop_stop()
        self._client.disconnect()
    
    def _send_message(self, message: FederatedActionMessage) -> bool:
        for topic in self._config.publish_topics:
            self._client.publish(
            topic=topic,
            payload=message.to_json(),
            qos=1,
            retain=False)
            self._logger.debug(f"Publishing message to topic {topic}: {message.to_json()}")
        return True
        



