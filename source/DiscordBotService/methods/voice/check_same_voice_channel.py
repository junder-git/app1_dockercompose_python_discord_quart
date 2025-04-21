"""
check_same_voice_channel method for Discord bot
Checks if a user is in the specified voice channel
"""

async def check_same_voice_channel(self, user, channel_id):
    """
    Check if a user is in the specified voice channel
    
    Args:
        user: Discord user object
        channel_id (str): Discord channel ID
        
    Returns:
        bool: True if user is in the specified channel, False otherwise
    """
    return user.voice and str(user.voice.channel.id) == channel_id