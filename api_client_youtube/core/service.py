import os
from datetime import timedelta
import types

from api_client_youtube.core.cache import CacheManager
from api_client_youtube.search.videos import search_videos
from api_client_youtube.search.playlists import search_playlists
from api_client_youtube.search.artists import search_artists
from api_client_youtube.details.video_details import get_video_details
from api_client_youtube.details.playlist_details import get_playlist_details
from api_client_youtube.details.playlist_videos import get_playlist_videos
from api_client_youtube.extractors.video_id import extract_video_id
from api_client_youtube.extractors.playlist_id import extract_playlist_id
from api_client_youtube.extractors.playlist_url import normalize_playlist_url
from api_client_youtube.extractors.duration import parse_duration, format_duration

class YouTubeService:
    """
    Centralized service for interacting with YouTube API
    Used by both Discord bot and Flask app
    """
    def __init__(self, api_key=None):
        # Get API key from environment or parameter
        self.api_key = api_key or os.environ.get('YOUTUBE_API_KEY')
        if not self.api_key:
            print("WARNING: No YouTube API key provided, YouTube API search will not work")
        
        # Cache settings
        self.cache_manager = CacheManager(timedelta(hours=1))
        
        # CRITICAL FIX: Apply audio extractors during initialization
        self._apply_audio_extractors()
    
    def _apply_audio_extractors(self):
        """
        Apply audio extraction methods directly to the instance
        This is called automatically during initialization
        """
        try:
            from api_client_youtube.extractors.audio_url import extract_audio_url, get_ffmpeg_options, process_youtube_url
            
            # Bind the functions to this instance
            self.extract_audio_url = types.MethodType(extract_audio_url, self)
            self.get_ffmpeg_options = types.MethodType(get_ffmpeg_options, self)
            self.process_youtube_url = types.MethodType(process_youtube_url, self)
            print("Audio extractors successfully applied to YouTubeService")
        except Exception as e:
            print(f"WARNING: Error applying audio extractors: {e}")
    
    async def search_videos(self, query, max_results=10):
        """
        Search YouTube for videos matching a query
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of video objects with id, title, thumbnail, channel
        """
        results = await search_videos(self.api_key, query, max_results, self.cache_manager)
        
        # FIX: Get video details to add duration for each search result
        if results:
            for result in results:
                try:
                    # Get full details including duration
                    details = await self.get_video_details(result['id'])
                    if details and 'duration' in details:
                        result['duration'] = details['duration']
                        result['duration_str'] = format_duration(details['duration'])
                except Exception as e:
                    print(f"Warning: Could not get duration for video {result['id']}: {e}")
                    result['duration'] = 0
                    result['duration_str'] = "00:00"
        
        return results
    
    async def search_playlists(self, query, max_results=5):
        """
        Search YouTube for playlists matching a query
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of playlist objects with id, title, thumbnail, channel
        """
        return await search_playlists(self.api_key, query, max_results, self.cache_manager)
    
    async def search_artists(self, query, max_results=10):
        """Search for YouTube channels (artists) based on a query"""
        return await search_artists(self.api_key, query, max_results)
    
    async def get_playlist_details(self, playlist_id):
        """
        Get details about a YouTube playlist
        
        Args:
            playlist_id (str): YouTube playlist ID
            
        Returns:
            dict: Playlist details including title, channel, thumbnail, video count
        """
        return await get_playlist_details(self.api_key, playlist_id, self.cache_manager)
    
    async def get_playlist_videos(self, playlist_id, page_token=None, max_results=25):
        """
        Get videos from a YouTube playlist with pagination support
        
        Args:
            playlist_id (str): YouTube playlist ID
            page_token (str, optional): Token for pagination
            max_results (int): Maximum results per page
            
        Returns:
            tuple: (videos, next_page_token, total_results)
        """
        results = await get_playlist_videos(self.api_key, playlist_id, page_token, max_results, self.cache_manager)
        
        # FIX: Add duration to playlist videos
        videos, next_page_token, total_results = results
        if videos:
            for video in videos:
                try:
                    # Get full details including duration
                    details = await self.get_video_details(video['id'])
                    if details and 'duration' in details:
                        video['duration'] = details['duration']
                        video['duration_str'] = format_duration(details['duration'])
                except Exception as e:
                    print(f"Warning: Could not get duration for video {video['id']}: {e}")
                    video['duration'] = 0
                    video['duration_str'] = "00:00"
        
        return videos, next_page_token, total_results
    
    async def get_video_details(self, video_id):
        """
        Get details about a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video details including title, channel, thumbnail, duration
        """
        details = await get_video_details(self.api_key, video_id, self.cache_manager)
        
        # FIX: Ensure duration is properly formatted
        if details and 'duration' in details:
            details['duration_str'] = format_duration(details['duration'])
        
        return details
    
    def extract_video_id(self, url):
        """
        Extract video ID from various YouTube URL formats
        
        Args:
            url (str): YouTube URL
            
        Returns:
            str: Video ID or None if not found
        """
        return extract_video_id(url)
    
    def extract_playlist_id(self, url):
        """
        Extract playlist ID from various YouTube playlist URL formats
        
        Args:
            url (str): YouTube URL
            
        Returns:
            str: Playlist ID or None if not found
        """
        return extract_playlist_id(url)
    
    def normalize_playlist_url(self, url):
        """
        Convert a video URL with playlist parameter to a playlist URL
        
        Args:
            url (str): Original YouTube URL
        
        Returns:
            str: Normalized playlist URL
        """
        return normalize_playlist_url(url)
    
    def parse_duration(self, duration_str):
        """
        Parse ISO 8601 duration to seconds
        e.g. PT1H30M15S -> 5415 seconds
        
        Args:
            duration_str (str): ISO 8601 duration string
            
        Returns:
            int: Duration in seconds
        """
        return parse_duration(duration_str)
    
    def format_duration(self, seconds):
        """
        Format duration in seconds to a readable string (MM:SS or HH:MM:SS)
        
        Args:
            seconds (int): Duration in seconds
            
        Returns:
            str: Formatted duration string
        """
        return format_duration(seconds)
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache_manager.clear_cache()


# Keep these functions for compatibility with existing code
def apply_audio_extractors(service):
    """
    Apply audio extraction methods to a YouTubeService instance
    
    Args:
        service: The YouTubeService instance
    """
    # Service now applies these by default, but keep the function
    # for backward compatibility
    if not hasattr(service, 'extract_audio_url'):
        service._apply_audio_extractors()
    
    return service


def apply_advanced_features(service):
    """
    Apply advanced feature methods to a YouTubeService instance
    
    Args:
        service: The YouTubeService instance
    """
    import asyncio
    
    async def get_playable_audio(self, url, quality='medium'):
        """
        Get everything needed to play audio from a YouTube URL in one call
        
        Args:
            url (str): YouTube URL or search query
            quality (str): Audio quality (low, medium, high)
            
        Returns:
            dict: Contains audio_url, ffmpeg_options, and video_details
        """
        # Extract video ID from URL or search for the video
        if url.startswith(('http://', 'https://')):
            video_id = self.extract_video_id(url)
            if not video_id:
                # Try processing as search or playlist
                processed = await self.process_youtube_url(url)
                if not processed or processed['type'] != 'video':
                    return None
                video_id = processed['info']['id']
        else:
            # Treat as search query
            search_results = await self.search_videos(url, max_results=1)
            if not search_results:
                return None
            video_id = search_results[0]['id']
        
        # Get audio URL and video details in parallel
        audio_url_task = asyncio.create_task(self.extract_audio_url(video_id))
        video_details_task = asyncio.create_task(self.get_video_details(video_id))
        
        audio_url = await audio_url_task
        video_details = await video_details_task
        ffmpeg_options = self.get_ffmpeg_options(quality)
        
        return {
            'audio_url': audio_url,
            'ffmpeg_options': ffmpeg_options,
            'video_details': video_details
        }
    
    # Only bind if not already present
    if not hasattr(service, 'get_playable_audio'):
        service.get_playable_audio = types.MethodType(get_playable_audio, service)
    
    return service


def create_youtube_service(api_key=None, apply_advanced=True):
    """
    Create and configure a YouTubeService instance with all necessary methods
    
    Args:
        api_key (str, optional): YouTube API key
        apply_advanced (bool): Apply advanced feature methods
        
    Returns:
        YouTubeService: Fully configured service instance
    """
    service = YouTubeService(api_key)
    
    # Audio extractors are now applied by default
    
    if apply_advanced:
        apply_advanced_features(service)
    
    return service