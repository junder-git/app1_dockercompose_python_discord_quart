import yt_dlp

async def extract_audio_url(video_id):
    """
    Extract direct audio URL for a YouTube video
    
    Args:
        video_id (str): YouTube video ID
        
    Returns:
        str: Direct audio URL or None if extraction failed
    """
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
            return audio_url
    except Exception as e:
        print(f"Error extracting audio URL for {video_id}: {e}")
        return None