
from dataclasses import dataclass, field
from typing import Type

from googly_eyes.transport import MessageTransport, EnabledMessageTransport
from googly_eyes.discord_interface import DiscordBotInterface, MockDiscordBotInterface


class GooglyEyesInstance:
    _transports: list[EnabledMessageTransport]
    _bot: DiscordBotInterface

    def __init__(self, bot) -> None:
        self._bot = bot
        self._transports = []

    
class GooglyEyesFactory:
    """Factory class for creating GooglyEyes instances."""
    
    @staticmethod
    def create(interface_type: Type[DiscordBotInterface], token: str) -> GooglyEyesInstance:
        """Create a new GooglyEyes instance."""
        instance = GooglyEyesInstance(bot=interface_type(token))
        return instance
    
    @staticmethod
    def create_mock_instance() -> GooglyEyesInstance:
        """Create a new mock GooglyEyes instance."""
        return GooglyEyesFactory.create(MockDiscordBotInterface, "mock_token")