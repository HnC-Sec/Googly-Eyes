from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from uuid import uuid4

class ModerationActionType(Enum):
    """Enum for moderation action types."""
    BAN = auto()
    KICK = auto()
    WARN = auto()
    TIMEOUT = auto()
    TRUST = auto()

class ActionReasonType(Enum):
    """Enum for action reason classifications."""
    SPAM = auto()
    HARASSMENT = auto()
    INAPPROPRIATE_CONTENT = auto()
    RULE_VIOLATION = auto()
    ABUSE = auto()
    DISRUPTIVE_BEHAVIOR = auto()
    OTHER = auto()

@dataclass
class BaseModerationAction(ABC):
    """Base class for moderation actions."""
    action_type: ModerationActionType
    target_user_id: str # Discord ID of the user being moderated
    action_moderator_id: str # Discord ID of the moderator taking the action
    action_reason: str # Reason for the action
    action_reason_type: ActionReasonType # Classification of the reason
    action_context: str|None = None # Context that caused the action
    action_timestamp: datetime = datetime.now(timezone.utc) # Timestamp of when the action was taken
    

class BanAction(BaseModerationAction):
    """Class for ban actions."""
    action_type: ModerationActionType = ModerationActionType.BAN
    can_appeal: bool = field(default=True) # Whether the user can appeal the ban


class KickAction(BaseModerationAction):
    """Class for kick actions."""
    action_type: ModerationActionType = field(default=ModerationActionType.KICK, init=False)

class WarnAction(BaseModerationAction):
    """Class for warn actions."""
    action_type: ModerationActionType = field(default=ModerationActionType.WARN, init=False)

class TimeoutAction(BaseModerationAction):
    """Class for timeout actions."""
    action_type: ModerationActionType = field(default=ModerationActionType.TIMEOUT, init=False)
    timeout_duration: int  # Duration in seconds

class TrustAction(BaseModerationAction):
    """Class for trust actions."""
    action_type: ModerationActionType = field(default=ModerationActionType.TRUST, init=False)

class ActionFactory:
    """Factory class for creating moderation actions."""
    
    @staticmethod
    def create_action(action_type: ModerationActionType, **kwargs) -> BaseModerationAction:
        """Create a moderation action based on the action type."""
        if action_type == ModerationActionType.BAN:
            return BanAction(action_type, **kwargs)
        elif action_type == ModerationActionType.KICK:
            return KickAction(action_type, **kwargs)
        elif action_type == ModerationActionType.WARN:
            return WarnAction(action_type, **kwargs)
        elif action_type == ModerationActionType.TIMEOUT:
            return TimeoutAction(action_type, **kwargs)
        elif action_type == ModerationActionType.TRUST:
            return TrustAction(action_type, **kwargs)
        else:
            raise ValueError(f"Unknown action type: {action_type}")

@dataclass
class FederatedActionMessage:
    """Class for federated action messages."""
    action: BaseModerationAction # The moderation action taken
    action_guild_id: str # Discord ID of the guild where the action is taken
    message_id: str = uuid4().hex # Unique identifier for the message
    message_timestamp: datetime = datetime.now(timezone.utc) # Timestamp of when the message was created