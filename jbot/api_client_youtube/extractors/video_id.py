import re

def extract_video_id(url):
    """
    Extract video ID from various YouTube URL formats
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: Video ID or None if not found
    """
    patterns = [
        r'(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})',  # Standard video URLs
        r'(?:embed/)([a-zA-Z0-9_-]{11})',  # Embed URLs
        r'(?:watch\?feature=player_embedded&v=)([a-zA-Z0-9_-]{11})'  # Feature player URLs
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None