import re

def extract_playlist_id(url):
    """
    Extract playlist ID from various YouTube playlist URL formats
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Playlist ID or None if not found
    """
    patterns = [
        r'list=([^&]+)',  # Captures list parameter in any URL
        r'playlist\?list=([^&]+)'  # Explicit playlist URL
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None