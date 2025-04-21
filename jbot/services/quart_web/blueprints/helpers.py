"""
Helper functions for routes in Quart Web Application
"""
import aiohttp
from functools import wraps
from quart import redirect, url_for, session, current_app
import os

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