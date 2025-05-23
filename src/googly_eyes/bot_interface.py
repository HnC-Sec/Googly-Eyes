from abc import ABC, abstractmethod, abstractproperty
from dataclasses import dataclass, field
from typing import Callable
from uuid import uuid4
from googly_eyes.models import BaseModerationAction
from logging import getLogger

@dataclass
class BotConfig(ABC):
    """Base class for bot configuration."""
    name: str = field(default_factory=lambda: f"{__name__}-{uuid4()}")

class BotInterface(ABC):
    """Base class for Discord bot interfaces."""
    def __init__(self, config: BotConfig) -> None:
        self._logger = getLogger(f"{__name__}-{config.name}")
        self._logger.debug("Initializing Discord bot interface.")
        self._is_running = False
        if not isinstance(config, self.config_type):
            raise ValueError(f"Invalid config type. Expected {self.config_type}, got {type(config)}.")
        self._config = config
        self._action_callback = None

    @property
    @abstractmethod
    def config_type(self) -> type[BotConfig]:
        """Return the type of the bot configuration."""
        raise NotImplementedError("Subclasses must implement this method.")

    def start(self) -> bool:
        """Start the Discord bot interface."""
        if not self._is_running:
            self._logger.info("Starting Discord bot interface.")
            self._is_running = self._start()
        return self._is_running
    
    @abstractmethod
    def _start(self) -> bool:
        """Start the Discord bot interface."""
        raise NotImplementedError("Subclasses must implement this method.")
    
    def stop(self) -> bool:
        """Stop the Discord bot interface."""
        if self._is_running:
            self._logger.info("Stopping Discord bot interface.")
            self._is_running = not self._stop()
        return not self._is_running

    @abstractmethod
    def _stop(self) -> bool:
        """Stop the Discord bot interface."""
        raise NotImplementedError("Subclasses must implement this method.")

    @property
    def running(self) -> bool:
        """Check if the Discord bot interface is running."""
        return self._is_running

    def set_action_callback(self, callback: Callable[[BaseModerationAction], None]) -> None:
        """Set a callback function to handle moderation actions."""
        self._logger.debug(f"Setting action callback [{callback}].")
        if not callable(callback):
            raise ValueError("Callback must be callable.")
        self._action_callback = callback

    def _propogate_action(self, action: BaseModerationAction) -> None:
        """Handle a moderation action."""
        if self._action_callback:
            self._action_callback(action)
        else:
            self._logger.warning("No action callback set. Action will not be processed.")

    @abstractmethod
    def do_action(self, action: BaseModerationAction, propogate: bool = True) -> None:
        """Perform a moderation action."""
        raise NotImplementedError("Subclasses must implement this method.")

class MockBotConfig(BotConfig):
    """Mock configuration for testing purposes."""
    
class MockBotInterface(BotInterface):
    """Mock implementation of the bot interface for testing purposes."""

    @property
    def config_type(self) -> type[BotConfig]:
        """Return the type of the bot configuration."""
        return MockBotConfig

    def _start(self) -> bool:
        self._logger.debug("Mock bot interface  started.")
        return True

    def _stop(self) -> bool:
        self._logger.debug("Mock bot interface stopped.")
        return True
    
    def fake_action(self, action: BaseModerationAction) -> None:
        """Simulate receiving a moderation action."""
        self._logger.debug(f"Mock action received: {action}")
        self._propogate_action(action)

    def do_action(self, action: BaseModerationAction, propogate: bool = True) -> None:
        """Perform a moderation action."""
        self._logger.debug(f"Mock action performed: {action}")
        if propogate:
            self.fake_action(action)
        else:
            self._logger.debug("Action not propagated.")