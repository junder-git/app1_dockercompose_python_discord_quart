"""
Audio Blueprint for Music Central Service
Handles audio extraction and processing
"""
from quart import Blueprint, request, current_app
import yt_dlp

# Create blueprint
audio_blueprint = Blueprint('audio', __name__, url_prefix='/api')

@audio_blueprint.route('/extract_audio', methods=['GET'])
async def extract_audio_route():
    """Extract audio URL from a YouTube video ID"""
    video_id = request.args.get('video_id')
    
    if not video_id:
        return {"error": "Missing video_id parameter"}, 400
    
    url = f"https://www.youtube.com/watch?v={video_id}"
    audio_url = await extract_audio_url(url)
    
    if not audio_url:
        return {"error": "Failed to extract audio URL"}, 404
    
    return {"audio_url": audio_url}

@audio_blueprint.route('/process_url', methods=['POST'])
async def process_url_route():
    """Process a YouTube URL, handling videos and playlists"""
    data = await request.get_json()
    url = data.get('url')
    
    if not url:
        return {"error": "Missing URL parameter"}, 400
    
    result = await process_youtube_url(url)
    
    if not result:
        return {"error": "Failed to process URL"}, 404
    
    return result

@audio_blueprint.route('/audio_options', methods=['GET'])
async def audio_options_route():
    """Get FFmpeg options for audio playback"""
    quality = request.args.get('quality', 'medium')
    
    # Make sure quality is one of the allowed values
    if quality not in ['low', 'medium', 'high']:
        quality = 'medium'
    
    options = get_ffmpeg_options(quality)
    
    return options


# Utility functions
async def extract_audio_url(url):
    """
    Extract direct audio URL for a YouTube video
    
    Args:
        url (str): YouTube video URL
        
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
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info.get('url')
            return audio_url
    except Exception as e:
        print(f"Error extracting audio URL for {url}: {e}")
        return None

async def process_youtube_url(url):
    """
    Process a YouTube URL, handling both individual videos and playlists
    
    Args:
        url (str): YouTube URL or search query
    
    Returns:
        dict: Result containing video or playlist information
    """
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'ignoreerrors': True,
        'no_color': True,
        'default_search': 'ytsearch',
        'max_downloads': 1
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

def get_ffmpeg_options(quality='medium'):
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