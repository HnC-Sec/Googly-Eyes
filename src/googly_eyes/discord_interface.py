from abc import ABC, abstractmethod
from typing import Callable
from googly_eyes.models import BaseModerationAction
from logging import getLogger


class DiscordBotInterface(ABC):
    """Base class for Discord bot interfaces."""

    def __init__(self, token: str) -> None:
        self._logger = getLogger(__name__)
        self._logger.debug("Initializing Discord bot interface.")
        self._is_running = False
        self._token = token
        self._action_callback = None

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

    def _handle_action(self, action: BaseModerationAction) -> None:
        """Handle a moderation action."""
        if self._action_callback:
            self._action_callback(action)
        else:
            self._logger.warning("No action callback set. Action will not be processed.")

class MockDiscordBotInterface(DiscordBotInterface):
    """Mock implementation of the Discord bot interface for testing purposes."""

    def _start(self) -> bool:
        self._logger.debug("Mock Discord bot interface started.")
        return True

    def _stop(self) -> bool:
        self._logger.debug("Mock Discord bot interface stopped.")
        return True
    
    def fake_action(self, action: BaseModerationAction) -> None:
        """Simulate receiving a moderation action."""
        self._logger.debug(f"Mock action received: {action}")
        self._handle_action(action)