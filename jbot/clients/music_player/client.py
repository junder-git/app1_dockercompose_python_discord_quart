"""
Music Player Client - Core client for music playback functionality
"""
import os
import yt_dlp
import aiohttp

class MusicPlayerClient:
    """Client for music playback functionality"""
    
    def __init__(self, host="music-central", port=5002, api_key=None):
        """
        Initialize the Music Player client
        
        Args:
            host (str): Music Central service host
            port (int): Music Central service port
            api_key (str, optional): YouTube API key for fallback behavior
        """
        self.base_url = f"http://{host}:{port}/api"
        self.api_key = api_key or os.environ.get('YOUTUBE_API_KEY')
        self.session = None
    
    async def ensure_session(self):
        """Ensure an aiohttp session exists, creating one if needed"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close the session when done"""
        if self.session:
            await self.session.close()
            self.session = None
    
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
            str: Direct audio URL or None if extraction failed
        """
        try:
            # First try to get the audio URL from the Music Central service
            await self.ensure_session()
            url = f"{self.base_url}/extract_audio?video_id={video_id}"
            
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if 'audio_url' in data:
                        return data['audio_url']
        except Exception as e:
            print(f"Error getting audio URL from service: {e}")
        
        # Fallback to direct extraction if service call fails
        return await self._fallback_extract_audio_url(video_id)
    
    async def _fallback_extract_audio_url(self, video_id):
        """
        Fallback method to extract audio URL directly
        
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
            'fragment_retries': 10,
            'retries': 10,
            'skip_unavailable_fragments': False,
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
    
    async def process_youtube_url(self, url):
        """
        Process a YouTube URL, handling both individual videos and playlists
        
        Args:
            url (str): YouTube URL or search query
        
        Returns:
            dict: Result containing video or playlist information
        """
        try:
            # Try to use the Music Central service
            await self.ensure_session()
            endpoint = f"{self.base_url}/process_url"
            
            async with self.session.post(endpoint, json={"url": url}) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            print(f"Error processing URL with service: {e}")
        
        # Fallback to direct extraction
        return await self._fallback_process_youtube_url(url)
    
    async def _fallback_process_youtube_url(self, url):
        """
        Fallback method to process YouTube URL directly
        
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
    
    async def search_videos(self, query, max_results=10):
        """
        Search for videos based on a query
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            list: List of video results
        """
        try:
            # Try to use the Music Central service
            await self.ensure_session()
            endpoint = f"{self.base_url}/search?q={query}&max_results={max_results}"
            
            async with self.session.get(endpoint) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('results', [])
        except Exception as e:
            print(f"Error searching with service: {e}")
        
        # Fallback to direct search
        return await self._fallback_search_videos(query, max_results)
    
    async def _fallback_search_videos(self, query, max_results=10):
        """
        Fallback method to search videos directly
        
        Args:
            query (str): Search query
            max_results (int): Maximum number of results
            
        Returns:
            list: List of video results
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'ignoreerrors': True,
            'no_color': True,
            'default_search': 'ytsearch',
            'max_downloads': max_results
        }
        
        search_query = f"ytsearch{max_results}:{query}"
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(search_query, download=False)
                
                if 'entries' in info:
                    results = []
                    for entry in info['entries']:
                        if entry:
                            results.append({
                                'id': entry.get('id'),
                                'title': entry.get('title', 'Unknown Title'),
                                'thumbnail': entry.get('thumbnail', ''),
                                'channel': entry.get('uploader', 'Unknown Channel'),
                                'duration': entry.get('duration', 0)
                            })
                    return results
        except Exception as e:
            print(f"Error in fallback search: {e}")
        
        return []