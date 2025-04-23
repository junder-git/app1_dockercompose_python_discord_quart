"""
Helper function to get queue and bot state
"""
from quart import current_app
from .get_voice_channels import get_voice_channels

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