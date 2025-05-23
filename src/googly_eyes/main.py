
from dataclasses import dataclass, field
from typing import Type

from googly_eyes.transport import MessageTransport, EnabledMessageTransport, MessageTransportConfig, MessageTransportFeatures, MockMessageTransport, MockMessageTransportConfig
from googly_eyes.bot_interface import BotConfig, BotInterface, MockBotConfig, MockBotInterface


class GooglyEyesInstance:
    _transports: list[EnabledMessageTransport]
    _bots: list[BotInterface]

    def __init__(self) -> None:
        self._bots: list[BotInterface] = []
        self._transports: list[EnabledMessageTransport] = []

    def add_bot(self, bot: BotInterface) -> None:
        """Add a bot to the GooglyEyes instance."""
        if not isinstance(bot, BotInterface):
            raise ValueError("Invalid bot type.")
        self._bots.append(bot)

    def add_transport(self, transport_type: Type[MessageTransport], config: MessageTransportConfig, enabled_features: MessageTransportFeatures | None = None, enabled: bool = True) -> None:
        """Add a transport to the GooglyEyes instance."""
        if not isinstance(enabled_features, MessageTransportFeatures):
            raise ValueError("Invalid features type.")
        
        transport = transport_type(config)
        emt = EnabledMessageTransport(transport)
        if enabled_features is None:
            enabled_features = transport._available_features
        emt.enable_feature(enabled_features)
        if enabled:
            emt.enable()
        self._transports.append(emt)

    def start(self) -> None:
        """Start the GooglyEyes instance."""
        for transport in self._transports:
            if not transport.start():
                raise RuntimeError(f"Failed to start transport {transport}.")
        for bot in self._bots:
            if not bot.start():
                raise RuntimeError(f"Failed to start bot {bot}.")

class GooglyEyesFactory:
    """Factory class for creating GooglyEyes instances."""
    
    @staticmethod
    def create_basic_instance(bot_interface_type: Type[BotInterface], bot_config: BotConfig) -> GooglyEyesInstance:
        """Create a new GooglyEyes instance."""
        instance = GooglyEyesInstance()
        instance.add_bot(bot_interface_type(bot_config))
        return instance
    
    @staticmethod
    def create_mock_instance() -> GooglyEyesInstance:
        """Create a new mock GooglyEyes instance."""
        instance = GooglyEyesFactory.create_basic_instance(MockBotInterface, MockBotConfig())
        instance.add_transport(MockMessageTransport, MockMessageTransportConfig(), MessageTransportFeatures.SEND_RECEIVE)
        return instance