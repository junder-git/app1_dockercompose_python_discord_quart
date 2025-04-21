"""
Discord API Client - Core client class
"""
import aiohttp
from urllib.parse import urlencode

class DiscordAPIClient:
    """Discord API Client for communication with the Discord Bot Service"""

    def __init__(self, host, port, secret_key):
        """
        Initialize the Discord Bot API client
        
        Args:
            host (str): API host address
            port (int): API port number
            secret_key (str): Authentication secret key
        """
        self.base_url = f"http://{host}:{port}/api"
        self.secret_key = secret_key
        self.session = None
    
    async def ensure_session(self):
        """Ensure an aiohttp session exists, creating one if needed"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _get_request(self, endpoint, params=None, default_response=None):
        """
        Generic method for GET requests
        
        Args:
            endpoint (str): API endpoint to call
            params (dict, optional): Query parameters
            default_response (dict, optional): Default response if the request fails
            
        Returns:
            dict: Response from the API or default/error response
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            url = f"{self.base_url}/{endpoint}"
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return default_response or {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API ({endpoint}): {e}")
            return default_response or {"success": False, "error": str(e)}
    
    async def _post_request(self, endpoint, data):
        """
        Generic method for POST requests
        
        Args:
            endpoint (str): API endpoint to call
            data (dict): Data to send in the request body
            
        Returns:
            dict: Response from the API or error response
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            url = f"{self.base_url}/{endpoint}"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API ({endpoint}): {e}")
            return {"success": False, "error": str(e)}
    
    # Public HTTP method wrappers for easier use in routes
    async def get(self, endpoint, params=None):
        """
        Public GET method wrapper for route handlers
        
        Args:
            endpoint (str): API endpoint path (can include query params)
            params (dict, optional): Additional query parameters
            
        Returns:
            Response: aiohttp ClientResponse object
        """
        await self.ensure_session()
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        
        # If endpoint already has query params, preserve them
        if '?' in endpoint and params:
            query_string = urlencode(params)
            url = f"{self.base_url}{endpoint}&{query_string}"
        elif params:
            query_string = urlencode(params)
            url = f"{self.base_url}{endpoint}?{query_string}"
        else:
            url = f"{self.base_url}{endpoint}"
            
        return await self.session.get(url, headers=headers)
    
    async def post(self, endpoint, data=None):
        """
        Public POST method wrapper for route handlers
        
        Args:
            endpoint (str): API endpoint path
            data (dict, optional): JSON data to send
            
        Returns:
            Response: aiohttp ClientResponse object
        """
        await self.ensure_session()
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        url = f"{self.base_url}{endpoint}"
        return await self.session.post(url, headers=headers, json=data)
    
    async def close(self):
        """Close the session when done"""
        if self.session:
            await self.session.close()
            self.session = None
            
    # Guild methods
    async def get_guild_count(self):
        """
        Get the count of guilds the bot is in
        
        Returns:
            int: Number of guilds
        """
        result = await self._get_request("guild_count")
        return result.get("count", 0)
    
    async def get_guild_ids(self):
        """
        Get the IDs of all guilds the bot is in
        
        Returns:
            list: List of guild IDs
        """
        result = await self._get_request("guild_ids")
        return result.get("guild_ids", [])
    
    # Queue methods
    async def get_queue(self, guild_id, channel_id=None):
        """
        Get the current queue for a guild
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str, optional): Discord channel ID
            
        Returns:
            dict: Queue information
        """
        params = {"guild_id": guild_id}
        if channel_id:
            params["channel_id"] = channel_id
            
        default_response = {
            "queue": [], 
            "current_track": None,
            "is_connected": False,
            "is_playing": False,
            "is_paused": False
        }
        
        result = await self._get_request("get_queue", params, default_response)
        
        # Ensure we have all the required fields with defaults
        if "queue" not in result:
            result["queue"] = []
        if "current_track" not in result:
            result["current_track"] = None
        if "is_connected" not in result:
            # Infer connection status from the current track
            result["is_connected"] = result.get("current_track") is not None
        if "is_playing" not in result:
            # Infer playing status
            result["is_playing"] = result.get("current_track") is not None
        if "is_paused" not in result:
            result["is_paused"] = False
            
        return result
    
    async def add_to_queue(self, guild_id, channel_id, video_id, video_title):
        """
        Add a track to the queue
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            video_id (str): YouTube video ID
            video_title (str): YouTube video title
            
        Returns:
            dict: Result of the operation
        """
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "video_id": video_id,
            "video_title": video_title
        }
        return await self._post_request("add_to_queue", data)
    
    async def add_multiple_to_queue(self, guild_id, channel_id, videos):
        """
        Add multiple tracks to the queue
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            videos (list): List of video dictionaries with 'id' and 'title' keys
            
        Returns:
            dict: Summary of the operation
        """
        # Track overall success
        overall_success = True
        added_count = 0
        error_messages = []
        
        # Add each video individually
        for video in videos:
            video_id = video.get('id')
            video_title = video.get('title', 'Unknown Video')
            
            result = await self.add_to_queue(guild_id, channel_id, video_id, video_title)
            
            if result.get('success'):
                added_count += 1
            else:
                overall_success = False
                error_messages.append(f"Error adding '{video_title}': {result.get('error')}")
        
        # Return a summary of the operation
        return {
            "success": overall_success or added_count > 0,  # Consider partial success as success
            "added_count": added_count,
            "total_count": len(videos),
            "message": f"Added {added_count} of {len(videos)} videos to queue",
            "errors": error_messages if error_messages else None
        }
    
    async def clear_queue(self, guild_id, channel_id=None):
        """
        Clear the queue for a guild
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str, optional): Discord channel ID
            
        Returns:
            dict: Result of the operation
        """
        data = {
            "guild_id": guild_id
        }
        if channel_id:
            data["channel_id"] = channel_id
        return await self._post_request("clear_queue", data)
    
    async def shuffle_queue(self, guild_id, channel_id):
        """
        Shuffle the queue for a guild
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            
        Returns:
            dict: Result of the operation
        """
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id
        }
        return await self._post_request("shuffle_queue", data)
    
    async def reorder_queue(self, guild_id, channel_id, old_index, new_index):
        """
        Reorder an item in the queue
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            old_index (int): Current position in the queue
            new_index (int): New position in the queue
            
        Returns:
            dict: Result of the operation
        """
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "old_index": old_index,
            "new_index": new_index
        }
        return await self._post_request("reorder_queue", data)
    
    # Playback methods
    async def skip_track(self, guild_id, channel_id):
        """
        Skip the current track in the queue
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            
        Returns:
            dict: Result of the operation
        """
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id
        }
        return await self._post_request("skip", data)
    
    async def pause_playback(self, guild_id, channel_id):
        """
        Pause the current playback
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            
        Returns:
            dict: Result of the operation
        """
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id
        }
        return await self._post_request("pause", data)
    
    async def resume_playback(self, guild_id, channel_id):
        """
        Resume the current playback
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            
        Returns:
            dict: Result of the operation
        """
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id
        }
        return await self._post_request("resume", data)
    
    # Voice methods
    async def join_voice_channel(self, guild_id, channel_id):
        """
        Join a voice channel in a guild
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord voice channel ID
            
        Returns:
            dict: Result of the join operation
        """
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "preserve_queue": True
        }
        return await self._post_request("join", data)
    
    async def disconnect_voice_channel(self, guild_id, user_id, preserve_queue=False):
        """
        Disconnect from a voice channel in a guild
        
        Args:
            guild_id (str): Discord guild ID
            user_id (str): Discord user ID requesting disconnect
            preserve_queue (bool): Whether to preserve the music queue
            
        Returns:
            dict: Result of the disconnect operation
        """
        data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "preserve_queue": preserve_queue
        }
        return await self._post_request("disconnect", data)
    
    # User methods
    async def get_user_voice_state(self, guild_id, user_id):
        """
        Get the voice state of a user in a guild
        
        Args:
            guild_id (str): Discord guild ID
            user_id (str): Discord user ID
            
        Returns:
            dict: Voice state information or None
        """
        params = {"guild_id": guild_id, "user_id": user_id}
        result = await self._get_request("get_user_voice_state", params)
        return result.get("voice_state")