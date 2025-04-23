"""
Discord API Client Blueprint
Provides a modular interface to communicate with the Discord bot API
"""
from quart import Blueprint

from .guild import GuildMethods
from .voice import VoiceMethods
from .queue import QueueMethods
from .playback import PlaybackMethods
from .user import UserMethods

# Create blueprint
discord_api_client_bp = Blueprint('discord_api_client', __name__)

"""
Base API class with core functionality for the Discord Bot API client
"""
import aiohttp

class ClientDiscordBotBase:
    def __init__(self, host, port, secret_key):
        """
        Initialize the Discord Bot API base class
        
        Args:
            host (str): API host address
            port (int): API port number
            secret_key (str): Authentication secret key
        """
        self.base_url = f"http://{host}:{port}/api"
        self.secret_key = secret_key
        self.session = None
    
    async def ensure_session(self):
        """Ensure an aiohttp session exists, creating one if needed"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _get_request(self, endpoint, params=None, default_response=None):
        """
        Generic method for GET requests
        
        Args:
            endpoint (str): API endpoint to call
            params (dict, optional): Query parameters
            default_response (dict, optional): Default response if the request fails
            
        Returns:
            dict: Response from the API or default/error response
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            url = f"{self.base_url}/{endpoint}"
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return default_response or {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API ({endpoint}): {e}")
            return default_response or {"success": False, "error": str(e)}
    
    async def _post_request(self, endpoint, data):
        """
        Generic method for POST requests
        
        Args:
            endpoint (str): API endpoint to call
            data (dict): Data to send in the request body
            
        Returns:
            dict: Response from the API or error response
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            url = f"{self.base_url}/{endpoint}"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API ({endpoint}): {e}")
            return {"success": False, "error": str(e)}
    
    async def close(self):
        """Close the session when done"""
        if self.session:
            await self.session.close()
            self.session = None

class ClientDiscordBot(ClientDiscordBotBase, 
                    GuildMethods,
                    VoiceMethods, 
                    QueueMethods, 
                    PlaybackMethods,
                    UserMethods):
    pass

# Factory function to create API client instance
def create_discord_bot_api(host, port, secret_key):
    """Create and return an instance of the Discord Bot API client"""
    return ClientDiscordBotBase(host, port, secret_key)