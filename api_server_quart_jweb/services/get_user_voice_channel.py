"""
Helper function to get user's current voice channel
"""
from quart import current_app
from .get_voice_channels import get_voice_channels

async def get_user_voice_channel(guild_id, user_id):
    """
    Get the voice channel a user is currently in
    
    Args:
        guild_id (str): Discord guild ID
        user_id (str): Discord user ID
    
    Returns:
        dict: Voice channel information including id and name, or None if not in a channel
    """
    
    try:
        # Try to get user voice state from bot API
        voice_state = await current_app.discord_api_client.get_user_voice_state(guild_id, user_id)
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