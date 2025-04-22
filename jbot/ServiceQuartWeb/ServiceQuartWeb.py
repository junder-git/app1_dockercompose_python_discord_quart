"""
Quart Web Service - Main entry point
"""
import os
import sys
from quart import Quart
from quart_discord import DiscordOAuth2Session
from quart_wtf import CSRFProtect
from dotenv import load_dotenv
import aiohttp
from functools import wraps
from quart import redirect, url_for, session, current_app

# Update path to find clients
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import clients
from clients.ClientDiscord import DiscordAPIClient
from clients.ClientYoutube import YouTubeClient

"""
Blueprints package for Quart Web Service
"""
from .index_blueprint import index_blueprint
from .auth_blueprint import auth_blueprint
from .dashboard_blueprint import dashboard_blueprint
from .server_blueprint import server_blueprint
from .search_blueprint import search_blueprint
from .queue_blueprint import queue_blueprint

__all__ = [
    'index_blueprint',
    'auth_blueprint',
    'dashboard_blueprint',
    'server_blueprint',
    'search_blueprint',
    'queue_blueprint'
]

"""
Helper functions for routes in Quart Web Application
"""


# Login required decorator
def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        print(f"Login check - Session contains: {list(session.keys())}")
        if 'user_id' not in session:
            print("No user_id in session, redirecting to login")
            return redirect(url_for('auth.login_route'))
        print(f"User {session.get('username')} authenticated, proceeding to route")
        return await f(*args, **kwargs)
    return decorated_function

async def get_voice_channels(guild_id):
    """Get voice channels for a guild"""
    discord_client = current_app.discord_client
    try:
        # First try to get voice channels from bot API
        response = await discord_client.get('/api/voice_channels')
        if response.status == 200:
            data = await response.json()
            channels = data.get('channels', [])
            return [c for c in channels if c.get('guild_id') == guild_id and c.get('type') == 2]
    except Exception as e:
        print(f"Error getting voice channels from bot API: {e}")
    
    # Fallback to direct Discord API call
    # Get bot token from environment variable
    DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
    headers = {'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
    channels = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://discord.com/api/guilds/{guild_id}/channels", 
            headers=headers
        ) as response:
            if response.status == 200:
                channels = await response.json()
    
    # Filter voice channels (type 2)
    return [c for c in channels if c['type'] == 2]

async def get_user_voice_channel(guild_id, user_id):
    """
    Get the voice channel a user is currently in
    
    Args:
        guild_id (str): Discord guild ID
        user_id (str): Discord user ID
    
    Returns:
        dict: Voice channel information including id and name, or None if not in a channel
    """
    discord_client = current_app.discord_client
    
    try:
        # Try to get user voice state from bot API
        voice_state = await discord_client.get_user_voice_state(guild_id, user_id)
        print(f"Voice state from bot API: {voice_state}")
        if voice_state and 'channel_id' in voice_state:
            channel_id = voice_state['channel_id']
            
            # Get all voice channels to find the channel name
            voice_channels = await get_voice_channels(guild_id)
            for channel in voice_channels:
                if channel['id'] == channel_id:
                    return channel
            
            # If channel not found in list, return minimal info
            return {'id': channel_id, 'name': 'Voice Channel'}
    except Exception as e:
        print(f"Error getting voice state: {e}")
    
    return None

async def get_queue_and_bot_state(guild_id, channel_id):
    """
    Get queue information and bot state for a specific channel
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        tuple: (queue_info, bot_state) containing queue and state information
    """
    if not channel_id:
        return {
            "queue": [], 
            "current_track": None
        }, {
            'connected': False,
            'is_playing': False,
            'voice_channel_id': None,
            'voice_channel_name': None
        }
    
    discord_client = current_app.discord_client
    
    try:
        queue_info = await discord_client.get_queue(guild_id, channel_id)
        
        # Get voice channels to find the channel name
        voice_channels = await get_voice_channels(guild_id)
        
        # Build bot state from queue info
        bot_state = {
            'connected': queue_info.get('is_connected', False),
            'is_playing': queue_info.get('is_playing', False),
            'voice_channel_id': channel_id,
            'voice_channel_name': 'Voice Channel'
        }
        
        # Find the voice channel name
        for channel in voice_channels:
            if channel['id'] == channel_id:
                bot_state['voice_channel_name'] = channel['name']
                break
                
        return queue_info, bot_state
        
    except Exception as e:
        print(f"Error getting queue and bot state: {e}")
        return {
            "queue": [], 
            "current_track": None
        }, {
            'connected': False,
            'is_playing': False,
            'voice_channel_id': channel_id,
            'voice_channel_name': 'Voice Channel'
        }

# Import blueprints
from quart_web.blueprints import (
    index_blueprint,
    auth_blueprint,
    dashboard_blueprint,
    server_blueprint,
    search_blueprint,
    queue_blueprint
)

# Load environment variables
load_dotenv()

# Configure the app and its dependencies
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Required for OAuth2 over http in development

# Get environment variables
SECRET_KEY = os.environ.get('SECRET_KEY')
DISCORD_CLIENT_ID = os.environ.get('DISCORD_CLIENT_ID')
DISCORD_CLIENT_SECRET = os.environ.get('DISCORD_CLIENT_SECRET')
DISCORD_REDIRECT_URI = os.environ.get('DISCORD_REDIRECT_URI')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Create the Quart app
app = Quart(__name__)
app.config.update(
    SECRET_KEY=SECRET_KEY,
    DISCORD_CLIENT_ID=DISCORD_CLIENT_ID,
    DISCORD_CLIENT_SECRET=DISCORD_CLIENT_SECRET,
    DISCORD_REDIRECT_URI=DISCORD_REDIRECT_URI,
    SESSION_COOKIE_SAMESITE='Lax',  # Important for OAuth redirect
    MAX_CONTENT_LENGTH=16 * 1024 * 1024  # 16MB max upload size
)

# Set defaults to avoid KeyErrors
app.config.setdefault("SECRET_KEY", SECRET_KEY)  # make sure this is set!
app.config.setdefault("WTF_CSRF_ENABLED", True)
app.config.setdefault("WTF_CSRF_CHECK_DEFAULT", True)
app.config.setdefault("WTF_CSRF_METHODS", ["POST", "PUT", "PATCH", "DELETE"])
app.config.setdefault("WTF_CSRF_TIME_LIMIT", 3600)
app.config.setdefault("WTF_CSRF_FIELD_NAME", "csrf_token")
app.config.setdefault("WTF_CSRF_HEADERS", ["X-CSRFToken", "X-CSRF-Token"])
app.config.setdefault("WTF_CSRF_SSL_STRICT", True)
app.config.setdefault("WTF_CSRF_SECRET_KEY", SECRET_KEY)

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize Discord OAuth
discord = DiscordOAuth2Session(app)
app.discord = discord

# Initialize API clients
app.discord_client = DiscordAPIClient(
    host="discord-bot",  # Docker service name
    port=5001,  # Port exposed in Docker
    secret_key=SECRET_KEY
)

app.youtube_client = YouTubeClient(api_key=YOUTUBE_API_KEY)

# Register application blueprints
app.register_blueprint(index_blueprint)
app.register_blueprint(auth_blueprint)
app.register_blueprint(dashboard_blueprint)
app.register_blueprint(server_blueprint)
app.register_blueprint(search_blueprint)
app.register_blueprint(queue_blueprint)

# Clean up on app exit
@app.teardown_appcontext
async def shutdown_session(exception=None):
    """Clean up resources when the app shuts down"""
    if hasattr(app, 'discord_client'):
        await app.discord_client.close()
    
    if hasattr(app, 'youtube_client'):
        app.youtube_client.clear_cache()

# Start the app
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=80)
