import yt_dlp

async def process_youtube_url(url):
    """
    Process a YouTube URL, handling both individual videos and playlists
    
    Args:
        url (str): YouTube URL or search query
    
    Returns:
        dict: One of these formats:
            - For single video: {'type': 'video', 'info': video_info}
            - For playlist: {'type': 'playlist', 'info': playlist_info, 'entries': playlist_entries}
            - For search query: {'type': 'video', 'info': video_info}
            - None if processing failed
    """
    # Configure yt-dlp options
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,  # Extract basic metadata without downloading
        'ignoreerrors': True,  # Continue processing if an individual video fails
        'no_color': True,
        'default_search': 'ytsearch',  # Ensure YouTube search
        'max_downloads': 1  # Limit to first result for non-URL input
    }
    
    # Check if the input looks like a URL
    def is_url(string):
        return string.startswith(('http://', 'https://'))
    
    # If not a URL, treat as a search query
    if not is_url(url):
        url = f"ytsearch1:{url}"
    
    # Use yt-dlp to extract information
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract information about the URL or search query
            info = ydl.extract_info(url, download=False)
            
            # Check if it's a playlist
            if 'entries' in info:
                # Validate it's actually a playlist (some YouTube URLs might look like playlists)
                entries = [entry for entry in info['entries'] if entry]
                
                if entries:
                    return {
                        'type': 'playlist',
                        'info': info,
                        'entries': entries
                    }
            
            # If not a playlist, treat as a single video
            if info and 'id' in info:
                return {
                    'type': 'video',
                    'info': info
                }
            
            # If no valid info found
            return None
        
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None