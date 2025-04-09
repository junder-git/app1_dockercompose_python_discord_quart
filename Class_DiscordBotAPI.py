import aiohttp

class DiscordBotAPI:
    def __init__(self, host, port, secret_key):
        self.base_url = f"http://{host}:{port}/api"
        self.secret_key = secret_key
        self.session = None
    
    async def ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def get_guild_count(self):
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            url = f"{self.base_url}/guild_count"
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return 0
                data = await response.json()
                return data.get("count", 0)
        except Exception as e:
            print(f"Error calling bot API (guild_count): {e}")
            return 0
    
    async def get_user_voice_state(self, guild_id, user_id):
        """
        Get the voice state of a user in a guild
        
        Args:
            guild_id (str): Discord guild ID
            user_id (str): Discord user ID
            
        Returns:
            dict: Voice state information or None if user is not in a voice channel
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            params = {
                "guild_id": guild_id,
                "user_id": user_id
            }
                    
            url = f"{self.base_url}/get_user_voice_state"
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return None
                    
                data = await response.json()
                return data.get("voice_state")
        except Exception as e:
            print(f"Error calling bot API (get_user_voice_state): {e}")
            return None

    async def get_guild_ids(self):
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            url = f"{self.base_url}/guild_ids"
            async with self.session.get(url, headers=headers) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return []
                data = await response.json()
                return data.get("guild_ids", [])
        except Exception as e:
            print(f"Error calling bot API (guild_ids): {e}")
            return []
            
    async def join_voice_channel(self, guild_id, channel_id):
        """Join a voice channel without affecting the queue"""
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "preserve_queue": True  # Add this flag to instruct the bot to preserve any existing queue
            }
            
            url = f"{self.base_url}/join"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (join_voice_channel): {e}")
            return {"success": False, "error": str(e)}
    
    
    
    
    
    
    
    
    async def disconnect_voice_channel(self, guild_id, user_id, preserve_queue=False):
        """Disconnect from the voice channel where the user is currently with the bot"""
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id,
                "user_id": user_id,
                "preserve_queue": preserve_queue
            }
            
            url = f"{self.base_url}/disconnect"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (disconnect_voice_channel): {e}")
            return {"success": False, "error": str(e)}
            
    
    
    
    
    
    
    async def add_to_queue(self, guild_id, channel_id, video_id, video_title):
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "video_id": video_id,
                "video_title": video_title
            }
            
            url = f"{self.base_url}/add_to_queue"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (add_to_queue): {e}")
            return {"success": False, "error": str(e)}

    async def get_queue(self, guild_id, channel_id=None):
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            params = {"guild_id": guild_id}
            if channel_id:
                params["channel_id"] = channel_id
                
            url = f"{self.base_url}/get_queue"
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {
                        "queue": [], 
                        "current_track": None,
                        "is_connected": False,
                        "is_playing": False,
                        "is_paused": False
                    }
                    
                # Get the queue data from the bot
                data = await response.json()
                
                # Ensure we have all the required fields with defaults
                if "queue" not in data:
                    data["queue"] = []
                if "current_track" not in data:
                    data["current_track"] = None
                if "is_connected" not in data:
                    # Infer connection status from the voice connections
                    data["is_connected"] = data.get("current_track") is not None
                if "is_playing" not in data:
                    # Infer playing status
                    data["is_playing"] = data.get("current_track") is not None
                if "is_paused" not in data:
                    data["is_paused"] = False
                    
                return data
        except Exception as e:
            print(f"Error calling bot API (get_queue): {e}")
            return {
                "queue": [], 
                "current_track": None,
                "is_connected": False,
                "is_playing": False,
                "is_paused": False
            }
            
    async def skip_track(self, guild_id, channel_id):
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id,
                "channel_id": channel_id
            }
            
            url = f"{self.base_url}/skip"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (skip_track): {e}")
            return {"success": False, "error": str(e)}
            
    async def pause_playback(self, guild_id, channel_id):
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id,
                "channel_id": channel_id
            }
            
            url = f"{self.base_url}/pause"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (pause_playback): {e}")
            return {"success": False, "error": str(e)}
            
    async def resume_playback(self, guild_id, channel_id):
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id,
                "channel_id": channel_id
            }
            
            url = f"{self.base_url}/resume"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (resume_playback): {e}")
            return {"success": False, "error": str(e)}









    async def clear_queue(self, guild_id):
        """Explicitly clear the queue for a guild without stopping playback"""
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id
            }
            
            url = f"{self.base_url}/clear_queue"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (clear_queue): {e}")
            return {"success": False, "error": str(e)}
    
    async def shuffle_queue(self, guild_id, channel_id):
        """Shuffle the music queue"""
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id,
                "channel_id": channel_id
            }
            
            url = f"{self.base_url}/shuffle_queue"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (shuffle_queue): {e}")
            return {"success": False, "error": str(e)}
    
    async def add_multiple_to_queue(self, guild_id, channel_id, videos):
        """
        Add multiple videos to the queue at once
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            videos (list): List of dictionaries with video_id and video_title keys
            
        Returns:
            dict: Response from the API
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            # Track overall success
            overall_success = True
            added_count = 0
            error_messages = []
            
            # Add each video individually since the bot API doesn't support batch adds yet
            for video in videos:
                video_id = video.get('id')
                video_title = video.get('title', 'Unknown Video')
                
                data = {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "video_id": video_id,
                    "video_title": video_title
                }
                
                url = f"{self.base_url}/add_to_queue"
                async with self.session.post(url, headers=headers, json=data) as response:
                    if response.status != 200:
                        overall_success = False
                        error_messages.append(f"Error adding '{video_title}': API error {response.status}")
                        continue
                    
                    result = await response.json()
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
        except Exception as e:
            print(f"Error calling bot API (add_multiple_to_queue): {e}")
            return {"success": False, "error": str(e)}
        

    async def reorder_queue(self, guild_id, channel_id, old_index, new_index):
        """
        Reorder the music queue by moving a track from one position to another
        
        Args:
            guild_id (str): Discord guild ID
            channel_id (str): Discord channel ID
            old_index (int): The current index of the track
            new_index (int): The new index to move the track to
            
        Returns:
            dict: Response from the API
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            data = {
                "guild_id": guild_id,
                "channel_id": channel_id,
                "old_index": old_index,
                "new_index": new_index
            }
            
            url = f"{self.base_url}/reorder_queue"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API (reorder_queue): {e}")
            return {"success": False, "error": str(e)}

    async def close(self):
        """Close the session when done"""
        if self.session:
            await self.session.close()
            self.session = None