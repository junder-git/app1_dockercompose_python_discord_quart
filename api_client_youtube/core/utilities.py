"""
Utility functions for the YouTube API client
"""

def format_duration(seconds):
    """
    Format duration in seconds to a readable string (HH:MM:SS)
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes}:{seconds:02d}"

def get_video_url(video_id):
    """
    Get the standard YouTube video URL for a video ID
    
    Args:
        video_id (str): YouTube video ID
        
    Returns:
        str: YouTube video URL
    """
    return f"https://www.youtube.com/watch?v={video_id}"

def get_playlist_url(playlist_id):
    """
    Get the standard YouTube playlist URL for a playlist ID
    
    Args:
        playlist_id (str): YouTube playlist ID
        
    Returns:
        str: YouTube playlist URL
    """
    return f"https://www.youtube.com/playlist?list={playlist_id}"

def get_channel_url(channel_id):
    """
    Get the standard YouTube channel URL for a channel ID
    
    Args:
        channel_id (str): YouTube channel ID
        
    Returns:
        str: YouTube channel URL
    """
    return f"https://www.youtube.com/channel/{channel_id}"