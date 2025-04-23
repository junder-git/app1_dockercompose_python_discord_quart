"""
Helper function to get voice channels
"""
import os
import aiohttp
from quart import current_app

async def get_voice_channels(guild_id):
    """
    Get voice channels for a guild
    
    Args:
        guild_id (str): Discord guild ID
        
    Returns:
        list: List of voice channel objects
    """
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