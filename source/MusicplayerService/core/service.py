from ClientYoutube import YouTubeService
from music_player_client.processors.url_processor import process_youtube_url
from music_player_client.processors.audio_processor import extract_audio_url
from music_player_client.search.video_search import search_videos
from music_player_client.config.audio_options import get_ffmpeg_options

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
        return await process_youtube_url(url)
    
    async def search_videos(self, query, max_results=10):
        """
        Search YouTube for videos matching a query with additional details
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of video objects with id, title, thumbnail, channel, duration
        """
        return await search_videos(self.api_key, query, max_results, self.youtube_service)
    
    def get_ffmpeg_options(self, quality='medium'):
        """
        Get FFmpeg options for audio playback
        
        Args:
            quality (str): Audio quality level (low, medium, high)
            
        Returns:
            dict: FFmpeg options
        """
        return get_ffmpeg_options(quality)
    
    async def extract_audio_url(self, video_id):
        """
        Extract direct audio URL for a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            str: Direct audio URL
        """
        return await extract_audio_url(video_id)