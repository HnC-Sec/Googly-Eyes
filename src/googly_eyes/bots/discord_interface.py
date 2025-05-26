from googly_eyes.bot_interface import BotInterface, BotConfig
from googly_eyes.models import ActionReasonType, BaseModerationAction, ModerationActionType
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Coroutine
from logging import getLogger
from discord import AuditLogAction, AuditLogEntry, Intents, Client
from discord.ext import commands



@dataclass
class DiscordBotConfig(BotConfig):
    """Configuration for the Discord bot interface."""
    token: str = field(default_factory=str)
    intents: Intents = field(default_factory=lambda: DiscordBotConfig.default_intents())

    @staticmethod
    def default_intents() -> Intents:
        """Return the default intents for the Discord bot."""
        intents = Intents.none()
        intents.moderation = True
        intents.members = True
        return intents
    
    
class DiscordBotInterface(BotInterface):
    """Discord bot interface for interacting with Discord servers."""
    _config: DiscordBotConfig

    @property
    def config_type(self) -> type[DiscordBotConfig]:
        """Return the type of the Discord bot configuration."""
        return DiscordBotConfig
    
    def __init__(self, config: DiscordBotConfig) -> None:
        super().__init__(config)
        self._bot = GooglyEyesBot(self, config)

    async def _start(self) -> bool:
        await self._bot.start(self._config.token)
        self._logger.info("Discord bot interface started.")
        return True

    async def _stop(self) -> bool:
        await self._bot.close()
        self._logger.info("Discord bot interface stopped.")
        return True

    async def do_action(self, action: BaseModerationAction, propogate: bool = True) -> None:
        pass

    async def handle_audit_log_entry(self, entry: AuditLogEntry) -> None:
        """Handle audit log entries."""
        self._logger.debug(f"Handling audit log entry: {entry}")
        match entry.action:
            case AuditLogAction.ban:
                action = BaseModerationAction(
                    action_type=ModerationActionType.BAN,
                    target_user_id=str(entry.target.id),
                    action_moderator_id=str(entry.user.id) or "Unknown",
                    action_reason=entry.reason or "Unknown",
                    action_reason_type=ActionReasonType.OTHER,
                )
            case _:
                self._logger.warning(f"Unhandled audit log action: {entry.action}")
                return
        await self._propogate_action(action)

class GooglyEyesBot(commands.Bot):
    """Custom Discord bot class for Googly Eyes."""
    
    def __init__(self, interface: DiscordBotInterface, config: DiscordBotConfig) -> None:
        super().__init__(command_prefix="!", intents=config.intents)
        self._logger = getLogger(f"{__name__}-{config.name}")
        self._logger.debug("Initializing Googly Eyes Discord bot.")
        self._interface = interface

    async def on_ready(self) -> None:
        """Event handler for when the bot is ready."""
        if self.user:
            self._logger.info(f"Logged in as {self.user.name} ({self.user.id})")

    async def on_audit_log_entry_create(self, entry) -> None:
        """Event handler for when an audit log entry is created."""
        self._logger.debug(f"Audit log entry created: {entry}")
        await self._interface.handle_audit_log_entry(entry)

    
        