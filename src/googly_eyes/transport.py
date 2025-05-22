from abc import ABC, abstractmethod
from typing import Callable

from googly_eyes.models import FederatedActionMessage


class MessageTransport(ABC):
    """Base class for message transport systems."""

    def __init__(self) -> None:
        self._receive_callback = None
        self._is_running = False

    def start(self) -> bool:
        """Start the transport system."""
        if not self._is_running:
            self._is_running = self._start()
        return self._is_running
            

    @abstractmethod
    def _start(self) -> bool:
        """Start listening for incoming messages."""
    
    def stop(self) -> bool:
        """Stop the transport system."""
        if self._is_running:
            self._is_running = not self._stop()
        return not self._is_running

    @abstractmethod
    def _stop(self) -> None:
        """Stop listening for incoming messages."""

    def send(self, message: FederatedActionMessage) -> bool:
        """Send a message to the transport system."""
        if not isinstance(message, FederatedActionMessage):
            raise ValueError("Invalid message type.")
        if not self._is_running:
            raise RuntimeError("Transport system is not running.")
        return self._send_message(message)

    @abstractmethod
    def _send_message(self, message: FederatedActionMessage) -> bool:
        """Send a message to the transport system."""

    def set_receive_callback(self, callback: Callable[[FederatedActionMessage, "MessageTransport"], None]) -> None:
        """Set a callback function to handle received messages."""
        if not callable(callback):
            raise ValueError("Callback must be callable.")
        self._receive_callback = callback
    
    def _message_received(self, message: FederatedActionMessage) -> None:
        """Handle a received message."""
        if self._receive_callback:
            self._receive_callback(message, self)
        else:
            raise ValueError("Receive callback not set.")