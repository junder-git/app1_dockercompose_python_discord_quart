import yt_dlp
import aiohttp
from source.Shared.Class_YouTube import YouTubeService

class MusicService:
    """
    Shared music service for processing YouTube URLs and handling music-related functionality
    Used by both Discord bot and Flask app
    """
    def __init__(self, api_key=None):
        self.api_key = api_key
        # Initialize YouTube service
        self.youtube_service = YouTubeService(api_key=self.api_key)
    
    async def process_youtube_url(self, url):
        """
        Process a YouTube URL, handling both individual videos and playlists
        
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
    
    async def search_videos(self, query, max_results=10):
        """
        Search YouTube for videos matching a query with additional details
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of video objects with id, title, thumbnail, channel, duration
        """
        # If no API key, return empty results
        if not self.api_key:
            return []
        
        search_results = []
        async with aiohttp.ClientSession() as session:
            # First, perform the search to get video IDs
            search_url = 'https://www.googleapis.com/youtube/v3/search'
            search_params = {
                'part': 'snippet',
                'q': query,
                'key': self.api_key,
                'maxResults': max_results,
                'type': 'video'
            }
            
            try:
                async with session.get(search_url, params=search_params) as search_response:
                    if search_response.status == 200:
                        search_data = await search_response.json()
                        
                        if 'items' in search_data:
                            # Extract video IDs
                            video_ids = [item['id']['videoId'] for item in search_data['items']]
                            
                            # Get details for these videos in a single API call
                            details_url = 'https://www.googleapis.com/youtube/v3/videos'
                            details_params = {
                                'part': 'snippet,contentDetails',
                                'id': ','.join(video_ids),
                                'key': self.api_key
                            }
                            
                            async with session.get(details_url, params=details_params) as details_response:
                                if details_response.status == 200:
                                    details_data = await details_response.json()
                                    
                                    # Create a mapping of video ID to details
                                    video_details = {
                                        item['id']: {
                                            'duration': YouTubeService().parse_duration(
                                                item['contentDetails'].get('duration', 'PT0S')
                                            ) if 'contentDetails' in item else 0
                                        } 
                                        for item in details_data.get('items', [])
                                    }
                                    
                                    # Combine search results with details
                                    for item in search_data['items']:
                                        video_id = item['id']['videoId']
                                        video = {
                                            'id': video_id,
                                            'title': item['snippet']['title'],
                                            'thumbnail': item['snippet']['thumbnails']['medium']['url'] 
                                                if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] 
                                                else '',
                                            'channel': item['snippet']['channelTitle'],
                                            'duration': video_details.get(video_id, {}).get('duration', 0)
                                        }
                                        search_results.append(video)
            except Exception as e:
                print(f"Error searching YouTube: {e}")
        
        return search_results
    
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
    
    async def extract_audio_url(self, video_id):
        """
        Extract direct audio URL for a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            str: Direct audio URL
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