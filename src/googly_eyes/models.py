from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum

class ModerationActionType(Enum):
    """Enum for moderation action types."""
    BAN = "ban"
    KICK = "kick"
    WARN = "warn"
    TIMEOUT = "timeout"
    TRUST = "trust"

@dataclass
class BaseModerationAction(ABC):
    """Base class for moderation actions."""
    action_type: ModerationActionType
    target_user_id: str # Discord ID of the user being moderated
    action_guild_id: str # Discord ID of the guild where the action is taken
    action_moderator_id: str # Discord ID of the moderator taking the action
    action_reason: str # Reason for the action
    action_context: str|None # Context that caused the action
    action_timestamp: datetime = field(default_factory=datetime.now(timezone.utc)) # Timestamp of when the action was taken
    

class BanAction(BaseModerationAction):
    """Class for ban actions."""
    action_type: ModerationActionType = field(default=ModerationActionType.BAN, init=False)
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
    trust_level: int  # Level of trust to assign
    