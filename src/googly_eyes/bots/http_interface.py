import asyncio
from dataclasses import dataclass
import enum
import aiohttp.web
from googly_eyes.bot_interface import BotInterface, BotConfig
import aiohttp

from googly_eyes.models import ActionFactory, BaseModerationAction, ModerationActionType

@dataclass
class HTTPBotConfig(BotConfig):
    """Configuration for the HTTP bot interface."""
    port: int = 8080
    host: str = "localhost"

class HTTPBotInterface(BotInterface):
    """HTTP bot interface for handling HTTP requests."""
    _config: HTTPBotConfig
    _server: aiohttp.web.Application

    def __init__(self, config: HTTPBotConfig) -> None:
        super().__init__(config)
        self._logger.debug("Initializing HTTP bot interface.")
        self._server = aiohttp.web.Application()
        self._taken_actions = []
        routes = [
            aiohttp.web.get('/', self.hello),
            aiohttp.web.get('/action', self.get_action),
            aiohttp.web.post('/action', self.post_action),
            ]
        self._server.add_routes(routes)
        
    @property
    def config_type(self) -> type[HTTPBotConfig]:
        return HTTPBotConfig

    async def _start(self) -> bool:
        """Start the HTTP server."""
        # Placeholder for starting the HTTP server
        self._logger.info(f"Starting HTTP server on {self._config.host}:{self._config.port}")
        self._runner = aiohttp.web.AppRunner(self._server)
        await self._runner.setup()
        self._site = aiohttp.web.TCPSite(self._runner, self._config.host, self._config.port)
        await self._site.start()
        return True

    async def _stop(self) -> bool:
        """Stop the HTTP server."""
        # Placeholder for stopping the HTTP server
        self._logger.info("Stopping HTTP server")
        await self._site.stop()
        await self._runner.cleanup()
        return True
    
    async def do_action(self, action: BaseModerationAction, propogate: bool = True) -> None:
        self._logger.debug(f"Performing action: {action}")
        self._taken_actions.append(action)

    async def hello(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle a simple hello world request."""
        return aiohttp.web.Response(text="Hello, world!")
    
    async def get_action(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle incoming GET requests for actions."""
        action_form = """
        <html>
        <body>
            <h1>Submit Moderation Action</h1>
            <form method="post" action="/action">
                <label for="action_type">Action Type:</label>
                <input type="text" id="action_type" name="action_type" required>
                <label for="target_user_id">Target User ID:</label>
                <input type="text" id="target_user_id" name="target_user_id" required>
                <label for="action_moderator_id">Moderator ID:</label>
                <input type="text" id="action_moderator_id" name="action_moderator_id" required>
                <label for="action_reason">Reason:</label>
                <input type="text" id="action_reason" name="action_reason" required>
                <label for="action_reason_type">Reason Type:</label>
                <input type="text" id="action_reason_type" name="action_reason_type" required>
                <button type="submit">Submit</button>
            </form>
        <div><h1>Taken Actions</h1></div>
            <ul>
    """ + "<br><br>".join(f"<li>{action}</li>" for action in self._taken_actions) + """
            </ul>
        </body>
        </html>
        """
        return aiohttp.web.Response(text=action_form, status=200, content_type='text/html')

    async def post_action(self, request: aiohttp.web.Request) -> aiohttp.web.Response:
        """Handle incoming moderation actions."""
        form_data = await request.text()
        data = {key:value for key, value in (item.split('=') for item in form_data.split('&'))}
        data['action_type'] =  ModerationActionType[data.get('action_type',"").upper()]
        action = ActionFactory.create_action(**data)
        self._logger.debug(f"Received action: {action}")
        await self._propogate_action(action)
        return aiohttp.web.Response(text="Action received", status=200)