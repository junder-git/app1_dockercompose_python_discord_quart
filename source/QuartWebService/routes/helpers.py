"""
Helper functions for routes in JBot Quart application
"""
import aiohttp
from functools import wraps
from quart import redirect, url_for, session
import os

# Get bot token from environment variable
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

# Login required decorator
def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        print(f"Login check - Session contains: {list(session.keys())}")
        if 'user_id' not in session:
            print("No user_id in session, redirecting to login")
            return redirect(url_for('login.login_route'))
        print(f"User {session.get('username')} authenticated, proceeding to route")
        return await f(*args, **kwargs)
    return decorated_function

async def get_voice_channels(guild_id):
    """Get voice channels for a guild"""
    headers = {'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
    channels = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://discord.com/api/guilds/{guild_id}/channels", 
            headers=headers
        ) as response:
            if response.status == 200:
                channels = await response.json()
    # Filter voice channels
    return [c for c in channels if c['type'] == 2]  # type 2 is voice channel

async def get_user_voice_channel(guild_id, user_id, bot_api):
    """
    Get the voice channel a user is currently in
    
    Args:
        guild_id (str): Discord guild ID
        user_id (str): Discord user ID
        bot_api: The bot API client instance
    
    Returns:
        dict: Voice channel information including id and name, or None if not in a channel
    """
    headers = {'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
    channel_id = None
    
    # Try getting from bot API first
    try:
        voice_state = await bot_api.get_user_voice_state(guild_id, user_id)
        print(f"Voice state from bot API: {voice_state}")
        if voice_state and 'channel_id' in voice_state:
            channel_id = voice_state['channel_id']
            print(f"Found voice channel ID from bot API: {channel_id}")
    except Exception as e:
        print(f"Error getting voice state from bot API: {e}")
    
    # If we couldn't get from bot API, try Discord API
    if not channel_id:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        member_data = await response.json()
                        # Try to find voice state information
                        print(f"Member data for {user_id}: {member_data}")
                        if 'voice' in member_data and member_data['voice'] and 'channel_id' in member_data['voice']:
                            channel_id = member_data['voice']['channel_id']
                            print(f"Found voice channel ID in member data: {channel_id}")
        except Exception as e:
            print(f"Error getting voice state from Discord API: {e}")
    
        # If we still couldn't get it, try voice states endpoint
        if not channel_id:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}",
                        headers=headers
                    ) as response: 
                        if response.status == 200:
                            voice_states = await response.json()
                            print(f"Voice states for guild {guild_id}: {voice_states}")
                            for state in voice_states:
                                if state.get('user_id') == user_id and state.get('channel_id'):
                                    channel_id = state.get('channel_id')
                                    print(f"Found voice channel ID in voice states: {channel_id}")
                                    break
            except Exception as e:
                print(f"Error getting voice states: {e}")
    
    # If we have a channel ID, get the channel details
    if channel_id:
        # Get all voice channels and find the one with matching ID
        try:
            voice_channels = await get_voice_channels(guild_id)
            for channel in voice_channels:
                if channel['id'] == channel_id:
                    print(f"Found matching voice channel details: {channel}")
                    return channel  # Return the full channel object with id, name, etc.
            
            # If we couldn't find the channel in the list (might happen if API is slow to update)
            print(f"Channel ID {channel_id} found but no matching channel in voice_channels list")
            return {'id': channel_id, 'name': 'Voice Channel'}
        except Exception as e:
            print(f"Error getting voice channel details: {e}")
            # If we can't get details, at least return the ID
            return {'id': channel_id, 'name': 'Voice Channel'}
    
    print(f"No voice channel found for user {user_id} in guild {guild_id}")
    return None

async def get_queue_and_bot_state(guild_id, selected_channel_id, voice_channels, bot_api):
    """Get queue information and bot state for a specific channel"""
    queue_info = {"queue": [], "current_track": None}
    bot_state = {
        'connected': False,
        'is_playing': False,
        'voice_channel_id': None,
        'voice_channel_name': None
    }
    
    if selected_channel_id:
        try:
            queue_info = await bot_api.get_queue(guild_id, selected_channel_id)
            
            # Update bot state based on queue info
            if queue_info.get('is_connected'):
                bot_state['connected'] = True
                bot_state['is_playing'] = queue_info.get('is_playing', False)
                
                # Find the voice channel name
                for channel in voice_channels:
                    if channel['id'] == selected_channel_id:
                        bot_state['voice_channel_id'] = channel['id']
                        bot_state['voice_channel_name'] = channel['name']
                        break
        except Exception as e:
            print(f"Error getting queue: {e}")
    
    return queue_info, bot_state