import re
from ClientYoutube.extractors.playlist_id import extract_playlist_id

def normalize_playlist_url(url):
    """
    Convert a video URL with playlist parameter to a playlist URL
    
    Args:
        url (str): Original YouTube URL
    
    Returns:
        str: Normalized playlist URL
    """
    # Extract playlist ID
    playlist_id = extract_playlist_id(url)
    
    if playlist_id:
        # Remove any video or index parameters
        url = re.sub(r'v=[^&]+', '', url)
        url = re.sub(r'index=\d+', '', url)
        url = re.sub(r'&{2,}', '&', url)  # Replace multiple consecutive & with single &
        url = url.rstrip('?&')  # Remove trailing ? or &
        
        # Construct a standard playlist URL
        return f"https://www.youtube.com/playlist?list={playlist_id}"
    
    return url  # Return original URL if no playlist ID found