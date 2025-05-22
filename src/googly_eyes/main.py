
from dataclasses import dataclass

from googly_eyes.transport import MessageTransport


@dataclass
class GooglyEyesInstance:
    _transport: MessageTransport