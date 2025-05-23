from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Flag
from typing import Callable

from googly_eyes.models import FederatedActionMessage

class MessageTransportFeatures(Flag):
    """Enum for message transport features."""

    NONE = 0
    SEND = 1
    RECEIVE = 2
    SEND_RECEIVE = SEND | RECEIVE


class MessageTransport(ABC):
    """Base class for message transport systems."""
    _available_features: MessageTransportFeatures = MessageTransportFeatures.NONE

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
        
    def feature_is_available(self, feature: MessageTransportFeatures) -> bool:
        """Check if a feature is available."""
        return feature in self._available_features
    
    @property
    def available_features(self) -> MessageTransportFeatures:
        """Get the available features of the transport."""
        return self._available_features


@dataclass
class EnabledMessageTransport:
    """Class to hold a message transport and its enabled status."""

    _transport: MessageTransport
    _enabled: bool = False
    _enabled_features: MessageTransportFeatures = MessageTransportFeatures.NONE

    def send(self, message: FederatedActionMessage) -> bool:
        """Send a message using the transport."""
        if not self._enabled or not self._enabled_features & MessageTransportFeatures.SEND:
            raise RuntimeError("Transport is not enabled for sending.")
        return self._transport.send(message)
    
    def set_receive_callback(self, callback: Callable[[FederatedActionMessage, MessageTransport], None]) -> None:
        """Set a receive callback for the transport."""
        if not self._enabled or not self._enabled_features & MessageTransportFeatures.RECEIVE:
            raise RuntimeError("Transport is not enabled for receiving.")
        self._transport.set_receive_callback(callback)

    def start(self) -> bool:
        """Start the transport."""
        if not self._enabled:
            raise RuntimeError("Transport is not enabled.")
        return self._transport.start()
    
    def stop(self) -> bool:
        """Stop the transport."""
        return self._transport.stop()
    
    @property
    def is_enabled(self) -> bool:
        """Check if the transport is enabled."""
        return self._enabled
    
    @property
    def enabled_features(self) -> MessageTransportFeatures:
        """Get the enabled features of the transport."""
        return self._enabled_features
    
    def enable(self) -> None:
        """Enable the transport."""
        self._enabled = True

    def disable(self) -> None:
        """Disable the transport."""
        self._enabled = False
        self.stop()

    def enable_feature(self, features: MessageTransportFeatures) -> None:
        """Set the enabled features of the transport."""
        if self._transport.feature_is_available(features):
            self._enabled_features |= features
        else:
            raise ValueError("Feature not available in transport.")