import yt_dlp

async def extract_audio_url(self, video_id_or_url):
    """
    Extract direct audio URL for a YouTube video
    
    Args:
        video_id_or_url (str): YouTube video ID or URL
        
    Returns:
        str: Direct audio URL
    """
    # Check if input is a URL or just a video ID
    if video_id_or_url.startswith(('http://', 'https://')):
        video_id = self.extract_video_id(video_id_or_url)
        if not video_id:
            print(f"Warning: Could not extract video ID from URL: {video_id_or_url}")
            return None
    else:
        video_id = video_id_or_url
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        # Add these options to ensure full song duration
        'fragment_retries': 10,
        'retries': 10,
        'skip_unavailable_fragments': False,
        # Add postprocessing to get consistent audio quality
        'postprocessor_args': [
            '-reconnect', '1',
            '-reconnect_streamed', '1',
            '-reconnect_delay_max', '5'
        ]
    }
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get('url')
            if not audio_url:
                print(f"Warning: No audio URL found for video ID: {video_id}")
            return audio_url
    except Exception as e:
        print(f"Error extracting audio URL for {video_id}: {e}")
        return None

def get_ffmpeg_options(self, quality='medium'):
    """
    Get FFmpeg options for audio playback
    
    Args:
        quality (str): Audio quality level (low, medium, high)
        
    Returns:
        dict: FFmpeg options
    """
    base_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    }
    
    if quality == 'low':
        base_options['options'] = '-vn -af "loudnorm=I=-16:TP=-1.5:LRA=11, aresample=48000, asetrate=48000*0.9"'
    elif quality == 'high':
        base_options['options'] = '-vn -af "loudnorm=I=-14:TP=-1:LRA=9" -b:a 192k'
    else:  # medium (default)
        base_options['options'] = '-vn -af "loudnorm=I=-16:TP=-1.5:LRA=11"'
        
    return base_options

async def process_youtube_url(self, url):
    """
    Process a YouTube URL, handling both individual videos and playlists
    
    Args:
        url (str): YouTube URL or search query
        
    Returns:
    - For single video: {'type': 'video', 'info': video_info}
    - For playlist: {'type': 'playlist', 'info': playlist_info, 'entries': playlist_entries}
    - For search query: {'type': 'video', 'info': video_info}
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
    if not url.startswith(('http://', 'https://')):
        url = f"ytsearch1:{url}"
    
    # Use yt-dlp to extract information
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            # Extract information about the URL or search query
            info = ydl.extract_info(url, download=False)
            
            # Check if it's a playlist
            if info and 'entries' in info:
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
            print(f"Warning: Could not process YouTube URL: {url}")
            return None
        
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return None