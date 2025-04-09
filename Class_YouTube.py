import os
import re
import aiohttp
from functools import lru_cache
from datetime import datetime, timedelta

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
        self.cache_timeout = timedelta(hours=1)  # Cache results for 1 hour
        self.cache_timestamp = {}  # Store timestamps for cache invalidation
    
    async def search_videos(self, query, max_results=10):
        """
        Search YouTube for videos matching a query
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of video objects with id, title, thumbnail, channel
        """
        # If no API key, return empty results
        if not self.api_key:
            return []
            
        cache_key = f"videos_{query}_{max_results}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        search_results = []
        async with aiohttp.ClientSession() as session:
            url = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'part': 'snippet',
                'q': query,
                'key': self.api_key,
                'maxResults': max_results,
                'type': 'video'
            }
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        results = await response.json()
                        if 'items' in results:
                            for item in results['items']:
                                video = {
                                    'id': item['id']['videoId'],
                                    'title': item['snippet']['title'],
                                    'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                                    'channel': item['snippet']['channelTitle']
                                }
                                search_results.append(video)
            except Exception as e:
                print(f"Error searching YouTube: {e}")
        
        # Cache results
        self._add_to_cache(cache_key, search_results)
        return search_results
    
    async def search_playlists(self, query, max_results=5):
        """
        Search YouTube for playlists matching a query
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of playlist objects with id, title, thumbnail, channel
        """
        # If no API key, return empty results
        if not self.api_key:
            return []
            
        cache_key = f"playlists_{query}_{max_results}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        search_results = []
        async with aiohttp.ClientSession() as session:
            url = 'https://www.googleapis.com/youtube/v3/search'
            params = {
                'part': 'snippet',
                'q': query,
                'key': self.api_key,
                'maxResults': max_results,
                'type': 'playlist'
            }
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        results = await response.json()
                        if 'items' in results:
                            for item in results['items']:
                                playlist = {
                                    'id': item['id']['playlistId'],
                                    'title': item['snippet']['title'],
                                    'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                                    'channel': item['snippet']['channelTitle']
                                }
                                search_results.append(playlist)
            except Exception as e:
                print(f"Error searching YouTube playlists: {e}")
        
        # Cache results
        self._add_to_cache(cache_key, search_results)
        return search_results
    
    async def get_playlist_details(self, playlist_id):
        """
        Get details about a YouTube playlist
        
        Args:
            playlist_id (str): YouTube playlist ID
            
        Returns:
            dict: Playlist details including title, channel, thumbnail, video count
        """
        # If no API key, return basic info
        if not self.api_key:
            return {
                'id': playlist_id,
                'title': 'Unknown Playlist',
                'channel': 'Unknown Channel',
                'thumbnail': '',
                'video_count': 0
            }
            
        cache_key = f"playlist_details_{playlist_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        async with aiohttp.ClientSession() as session:
            url = 'https://www.googleapis.com/youtube/v3/playlists'
            params = {
                'part': 'snippet,contentDetails',
                'id': playlist_id,
                'key': self.api_key
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        results = await response.json()
                        if 'items' in results and len(results['items']) > 0:
                            item = results['items'][0]
                            
                            # Extract playlist details
                            details = {
                                'id': playlist_id,
                                'title': item['snippet']['title'],
                                'channel': item['snippet']['channelTitle'],
                                'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                                'video_count': item['contentDetails']['itemCount'] if 'contentDetails' in item and 'itemCount' in item['contentDetails'] else 0
                            }
                            
                            # Cache the result
                            self._add_to_cache(cache_key, details)
                            return details
            except Exception as e:
                print(f"Error getting playlist details: {e}")
        
        # Return default values if something went wrong
        default_details = {
            'id': playlist_id,
            'title': 'Unknown Playlist',
            'channel': 'Unknown Channel',
            'thumbnail': '',
            'video_count': 0
        }
        
        # Still cache the default to prevent repeated API failures
        self._add_to_cache(cache_key, default_details)
        return default_details
    
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
        # If no API key, return empty results
        if not self.api_key:
            return [], None, 0
            
        # For playlists, we don't cache results with page tokens to avoid complexity
        cache_key = f"playlist_videos_{playlist_id}"
        if page_token is None:
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
        
        videos = []
        next_page_token = None
        total_results = 0
        
        async with aiohttp.ClientSession() as session:
            url = 'https://www.googleapis.com/youtube/v3/playlistItems'
            params = {
                'part': 'snippet,contentDetails',
                'playlistId': playlist_id,
                'key': self.api_key,
                'maxResults': max_results
            }
            
            # Add page token if provided
            if page_token:
                params['pageToken'] = page_token
                
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        results = await response.json()
                        
                        # Get total results and next page token
                        if 'pageInfo' in results and 'totalResults' in results['pageInfo']:
                            total_results = results['pageInfo']['totalResults']
                        
                        if 'nextPageToken' in results:
                            next_page_token = results['nextPageToken']
                        
                        if 'items' in results:
                            for item in results['items']:
                                # Get video details - sometimes videoId is in different locations
                                video_id = None
                                if 'contentDetails' in item and 'videoId' in item['contentDetails']:
                                    video_id = item['contentDetails']['videoId']
                                elif 'snippet' in item and 'resourceId' in item['snippet'] and 'videoId' in item['snippet']['resourceId']:
                                    video_id = item['snippet']['resourceId']['videoId']
                                
                                if video_id:
                                    video = {
                                        'id': video_id,
                                        'title': item['snippet']['title'],
                                        'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                                        'channel': item['snippet']['channelTitle'] if 'channelTitle' in item['snippet'] else 'Unknown'
                                    }
                                    videos.append(video)
            except Exception as e:
                print(f"Error getting playlist videos: {e}")
        
        # Only cache first page results (without page token)
        result = (videos, next_page_token, total_results)
        if page_token is None:
            self._add_to_cache(cache_key, result)
        
        return result
    
    async def get_video_details(self, video_id):
        """
        Get details about a YouTube video
        
        Args:
            video_id (str): YouTube video ID
            
        Returns:
            dict: Video details including title, channel, thumbnail, duration
        """
        # If no API key, return basic info
        if not self.api_key:
            return {
                'id': video_id,
                'title': 'Unknown Video',
                'channel': 'Unknown Channel',
                'thumbnail': '',
                'duration': 0
            }
            
        cache_key = f"video_details_{video_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
            
        async with aiohttp.ClientSession() as session:
            url = 'https://www.googleapis.com/youtube/v3/videos'
            params = {
                'part': 'snippet,contentDetails',
                'id': video_id,
                'key': self.api_key
            }
            
            try:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        results = await response.json()
                        if 'items' in results and len(results['items']) > 0:
                            item = results['items'][0]
                            
                            # Parse duration from ISO 8601 format
                            duration_str = item['contentDetails']['duration'] if 'contentDetails' in item and 'duration' in item['contentDetails'] else 'PT0S'
                            duration_seconds = self.parse_duration(duration_str)
                            
                            # Extract video details
                            details = {
                                'id': video_id,
                                'title': item['snippet']['title'],
                                'channel': item['snippet']['channelTitle'],
                                'thumbnail': item['snippet']['thumbnails']['medium']['url'] if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] else '',
                                'duration': duration_seconds
                            }
                            
                            # Cache the result
                            self._add_to_cache(cache_key, details)
                            return details
            except Exception as e:
                print(f"Error getting video details: {e}")
        
        # Return default values if something went wrong
        default_details = {
            'id': video_id,
            'title': 'Unknown Video',
            'channel': 'Unknown Channel',
            'thumbnail': '',
            'duration': 0
        }
        
        # Still cache the default to prevent repeated API failures
        self._add_to_cache(cache_key, default_details)
        return default_details
    
    def extract_video_id(self, url):
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
    
    def extract_playlist_id(self, url):
        """
        Extract playlist ID from various YouTube playlist URL formats
        
        Args:
            url (str): YouTube URL
            
        Returns:
            str: Playlist ID or None if not found
        """
        patterns = [
            r'list=([^&]+)',  # Captures list parameter in any URL
            r'playlist\?list=([^&]+)'  # Explicit playlist URL
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def normalize_playlist_url(self, url):
        """
        Convert a video URL with playlist parameter to a playlist URL
        
        Args:
            url (str): Original YouTube URL
        
        Returns:
            str: Normalized playlist URL
        """
        # Extract playlist ID
        playlist_id = self.extract_playlist_id(url)
        
        if playlist_id:
            # Remove any video or index parameters
            url = re.sub(r'v=[^&]+', '', url)
            url = re.sub(r'index=\d+', '', url)
            url = re.sub(r'&{2,}', '&', url)  # Replace multiple consecutive & with single &
            url = url.rstrip('?&')  # Remove trailing ? or &
            
            # Construct a standard playlist URL
            return f"https://www.youtube.com/playlist?list={playlist_id}"
        
        return url  # Return original URL if no playlist ID found
    
    def parse_duration(self, duration_str):
        """
        Parse ISO 8601 duration to seconds
        e.g. PT1H30M15S -> 5415 seconds
        
        Args:
            duration_str (str): ISO 8601 duration string
            
        Returns:
            int: Duration in seconds
        """
        hours = 0
        minutes = 0
        seconds = 0
        
        # Extract hours
        hour_match = re.search(r'(\d+)H', duration_str)
        if hour_match:
            hours = int(hour_match.group(1))
        
        # Extract minutes
        minute_match = re.search(r'(\d+)M', duration_str)
        if minute_match:
            minutes = int(minute_match.group(1))
        
        # Extract seconds
        second_match = re.search(r'(\d+)S', duration_str)
        if second_match:
            seconds = int(second_match.group(1))
        
        return hours * 3600 + minutes * 60 + seconds
    
    def _get_from_cache(self, key):
        """Get a value from cache if it exists and is not expired"""
        if key in self.cache_timestamp:
            # Check if cache is expired
            if datetime.now() - self.cache_timestamp[key] < self.cache_timeout:
                try:
                    return getattr(self, f"_cache_{key}")
                except AttributeError:
                    return None
            else:
                # Expired, clean up
                try:
                    delattr(self, f"_cache_{key}")
                except AttributeError:
                    pass
                self.cache_timestamp.pop(key, None)
        return None
    
    def _add_to_cache(self, key, value):
        """Add a value to cache with current timestamp"""
        setattr(self, f"_cache_{key}", value)
        self.cache_timestamp[key] = datetime.now()
    
    def clear_cache(self):
        """Clear all cached data"""
        for key in list(self.cache_timestamp.keys()):
            try:
                delattr(self, f"_cache_{key}")
            except AttributeError:
                pass
        self.cache_timestamp.clear()