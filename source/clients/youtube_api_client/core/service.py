import os
from datetime import timedelta

from youtube_api_client.core.cache import CacheManager
from youtube_api_client.search.videos import search_videos
from youtube_api_client.search.playlists import search_playlists
from youtube_api_client.search.artists import search_artists
from youtube_api_client.details.video_details import get_video_details
from youtube_api_client.details.playlist_details import get_playlist_details
from youtube_api_client.details.playlist_videos import get_playlist_videos
from youtube_api_client.extractors.video_id import extract_video_id
from youtube_api_client.extractors.playlist_id import extract_playlist_id
from youtube_api_client.extractors.playlist_url import normalize_playlist_url
from youtube_api_client.extractors.duration import parse_duration

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
    
    async def search_videos(self, query, max_results=10):
        """
        Search YouTube for videos matching a query
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of video objects with id, title, thumbnail, channel
        """
        return await search_videos(self.api_key, query, max_results, self.cache_manager)
    
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
        return await get_playlist_videos(self.api_key, playlist_id, page_token, max_results, self.cache_manager)
    
    async def get_video_details(self, video_id):
        """
        Get details about a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video details including title, channel, thumbnail, duration
        """
        return await get_video_details(self.api_key, video_id, self.cache_manager)
    
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
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache_manager.clear_cache()