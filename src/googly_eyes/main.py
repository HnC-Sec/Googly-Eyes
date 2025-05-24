
import asyncio
from dataclasses import dataclass, field
from logging import getLogger, basicConfig, DEBUG
import signal
from typing import Type

from googly_eyes.bots.http_interface import HTTPBotConfig, HTTPBotInterface
from googly_eyes.models import BaseModerationAction
from googly_eyes.transport import MessageTransport, EnabledMessageTransport, MessageTransportConfig, MessageTransportFeatures, MockMessageTransport, MockMessageTransportConfig, FederatedActionMessage
from googly_eyes.bot_interface import BotConfig, BotInterface, MockBotConfig, MockBotInterface


class GooglyEyesInstance:
    _transports: list[EnabledMessageTransport]
    _bots: list[BotInterface]
    _running: bool = False

    def __init__(self) -> None:
        basicConfig(level=DEBUG)
        self._logger = getLogger(__name__)
        self._bots: list[BotInterface] = []
        self._transports: list[EnabledMessageTransport] = []
        self._event_loop = asyncio.new_event_loop()

    def add_bot(self, bot: BotInterface) -> None:
        """Add a bot to the GooglyEyes instance."""
        if not isinstance(bot, BotInterface):
            raise ValueError("Invalid bot type.")
        bot.set_action_callback(self.handle_bot_action)
        self._bots.append(bot)

    async def handle_bot_action(self, action: BaseModerationAction, source: BotInterface) -> None:
        """Handle incoming actions from the bot."""
        self._logger.debug(f"Handling action from bot: {action}")
        for transport in self._transports:
            if transport.is_enabled and MessageTransportFeatures.SEND in transport.enabled_features:
                transport.send(FederatedActionMessage(action=action, action_guild_id=source._config.name))
                self._logger.debug(f"Sent action {action} to transport {transport}")
        for bot in self._bots:
            if bot.running and bot != source:
                await bot.do_action(action, propogate=False)
                self._logger.debug(f"Propagated action {action} to bot {bot._config.name}")
        

    def add_transport(self, transport_type: Type[MessageTransport], config: MessageTransportConfig, enabled_features: MessageTransportFeatures | None = None, enabled: bool = True) -> None:
        """Add a transport to the GooglyEyes instance."""
        if not isinstance(enabled_features, MessageTransportFeatures):
            raise ValueError("Invalid features type.")
        
        transport = transport_type(config)
        transport.set_receive_callback(self.handle_transport_message)
        emt = EnabledMessageTransport(transport)
        if enabled_features is None:
            enabled_features = transport._available_features
        emt.enable_feature(enabled_features)
        if enabled:
            emt.enable()
        self._transports.append(emt)

    async def handle_transport_message(self, message: FederatedActionMessage, transport: MessageTransport) -> None:
        """Handle incoming messages from the transport."""
        self._logger.debug(f"Handling message from transport: {message}")
        for bot in self._bots:
            if bot.running:
                await bot.do_action(message.action, propogate=False)
                self._logger.debug(f"Propagated message {message} to bot {bot._config.name}")

    async def start(self) -> None:
        """Start the GooglyEyes instance."""
        for transport in self._transports:
            if not transport.start():
                raise RuntimeError(f"Failed to start transport {transport}.")
        for bot in self._bots:
            if not await bot.start():
                raise RuntimeError(f"Failed to start bot {bot}.")
        self._running = True

    def stop(self) -> None:
        """Stop the GooglyEyes instance."""
        for bot in self._bots:
            self._event_loop.create_task(bot.stop())
        for transport in self._transports:
            transport.stop()
        self._running = False

    async def main_loop(self) -> None:
        await self.start()
        while self._running:
            await asyncio.sleep(1)
            self._logger.debug("Main loop running...")
        self._event_loop.stop()

    def async_run(self) -> None:
        """Run the GooglyEyes instance."""
        self._event_loop.add_signal_handler(signal.SIGINT, self.stop)
        self._event_loop.create_task(self.main_loop())
        self._event_loop.run_forever()



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
    
if __name__ == "__main__":
    # Example usage
    instance = GooglyEyesFactory.create_basic_instance(HTTPBotInterface, HTTPBotConfig(port=8080, host="localhost"))
    instance.add_bot(HTTPBotInterface(HTTPBotConfig(port=8081, host="localhost")))
    instance.add_transport(MockMessageTransport, MockMessageTransportConfig(), MessageTransportFeatures.SEND_RECEIVE)
    instance.async_run()