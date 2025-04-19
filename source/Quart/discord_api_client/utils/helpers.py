"""
Helper functions for Discord API client
"""

def format_duration(seconds):
    """
    Format seconds into a human-readable duration
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Formatted duration string (MM:SS or HH:MM:SS)
    """
    if seconds is None:
        return "00:00"
        
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"

def create_queue_id(guild_id, channel_id):
    """
    Create a queue ID from guild and channel IDs
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        str: Queue ID
    """
    return f"{guild_id}:{channel_id}"