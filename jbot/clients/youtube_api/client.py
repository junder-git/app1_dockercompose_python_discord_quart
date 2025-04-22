"""
YouTube API Client - Core client for YouTube API interaction
"""
import os
import re
import aiohttp
from datetime import datetime, timedelta
import yt_dlp

class YouTubeClient:
    """Client for YouTube API interactions"""
    
    def __init__(self, api_key=None):
        """
        Initialize the YouTube API client
        
        Args:
            api_key (str, optional): YouTube API key, falls back to environment variable
        """
        # Get API key from environment or parameter
        self.api_key = api_key or os.environ.get('YOUTUBE_API_KEY')
        if not self.api_key:
            print("WARNING: No YouTube API key provided, YouTube API search will not work")
        
        # Cache settings
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_timeout = timedelta(hours=1)
    
    def _get_from_cache(self, key):
        """
        Get a value from cache if it exists and is not expired
        
        Args:
            key (str): Cache key
            
        Returns:
            object: Cached value or None if not found or expired
        """
        if key in self.cache_timestamps:
            # Check if cache is expired
            if datetime.now() - self.cache_timestamps[key] < self.cache_timeout:
                return self.cache.get(key)
            else:
                # Expired, clean up
                self.cache.pop(key, None)
                self.cache_timestamps.pop(key, None)
        return None
    
    def _add_to_cache(self, key, value):
        """
        Add a value to cache with current timestamp
        
        Args:
            key (str): Cache key
            value (object): Value to cache
        """
        self.cache[key] = value
        self.cache_timestamps[key] = datetime.now()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.cache_timestamps.clear()
    
    async def search_videos(self, query, max_results=10):
        """
        Search YouTube for videos matching a query
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results to return
            
        Returns:
            list: List of video objects with id, title, thumbnail, channel
        """
        # Check cache first
        cache_key = f"videos_{query}_{max_results}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # If no API key, return empty results
        if not self.api_key:
            return []
        
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
                                    'thumbnail': item['snippet']['thumbnails']['medium']['url'] 
                                        if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] 
                                        else '',
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
        # Check cache first
        cache_key = f"playlists_{query}_{max_results}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # If no API key, return empty results
        if not self.api_key:
            return []
        
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
                                    'thumbnail': item['snippet']['thumbnails']['medium']['url'] 
                                        if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] 
                                        else '',
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
        # Check cache first
        cache_key = f"playlist_details_{playlist_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # If no API key, return basic info
        if not self.api_key:
            return {
                'id': playlist_id,
                'title': 'Unknown Playlist',
                'channel': 'Unknown Channel',
                'thumbnail': '',
                'video_count': 0
            }
        
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
                                'thumbnail': item['snippet']['thumbnails']['medium']['url'] 
                                    if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] 
                                    else '',
                                'video_count': item['contentDetails']['itemCount'] 
                                    if 'contentDetails' in item and 'itemCount' in item['contentDetails'] 
                                    else 0
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
        # For playlists, we don't cache results with page tokens to avoid complexity
        cache_key = f"playlist_videos_{playlist_id}"
        
        # Try to get from cache if no page token
        if page_token is None:
            cached_result = self._get_from_cache(cache_key)
            if cached_result is not None:
                return cached_result
        
        # If no API key, return empty results
        if not self.api_key:
            return [], None, 0
        
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
                                        'thumbnail': item['snippet']['thumbnails']['medium']['url'] 
                                            if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] 
                                            else '',
                                        'channel': item['snippet']['channelTitle'] 
                                            if 'channelTitle' in item['snippet'] 
                                            else 'Unknown'
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
        # Check cache first
        cache_key = f"video_details_{video_id}"
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # If no API key, return basic info
        if not self.api_key:
            return {
                'id': video_id,
                'title': 'Unknown Video',
                'channel': 'Unknown Channel',
                'thumbnail': '',
                'duration': 0
            }
        
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
                                'thumbnail': item['snippet']['thumbnails']['medium']['url'] 
                                    if 'thumbnails' in item['snippet'] and 'medium' in item['snippet']['thumbnails'] 
                                    else '',
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
    
    def format_duration(self, seconds):
        """
        Format duration in seconds to a readable string (MM:SS or HH:MM:SS)
        
        Args:
            seconds (int): Duration in seconds
            
        Returns:
            str: Formatted duration string
        """
        if seconds is None:
            return "00:00"
            
        minutes, seconds = divmod(int(seconds), 60)
        hours, minutes = divmod(minutes, 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
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