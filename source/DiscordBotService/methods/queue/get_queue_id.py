"""
get_queue_id method for Discord bot
Creates a unique queue ID from guild and channel IDs
"""

def get_queue_id(self, guild_id, channel_id):
    """
    Create a unique queue ID from guild and channel IDs
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        str: A unique queue ID combining guild and channel IDs
    """
    return f"{guild_id}_{channel_id}"