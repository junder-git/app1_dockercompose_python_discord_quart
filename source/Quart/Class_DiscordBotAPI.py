import aiohttp

class DiscordBotAPI:
    def __init__(self, host, port, secret_key):
        self.base_url = f"http://{host}:{port}/api"
        self.secret_key = secret_key
        self.session = None
    
    async def ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _get_request(self, endpoint, params=None, default_response=None):
        """Generic method for GET requests"""
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
        """Generic method for POST requests"""
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
    
    # Guild information methods
    async def get_guild_count(self):
        result = await self._get_request("guild_count")
        return result.get("count", 0)
    
    async def get_guild_ids(self):
        result = await self._get_request("guild_ids")
        return result.get("guild_ids", [])
    
    # User state methods
    async def get_user_voice_state(self, guild_id, user_id):
        params = {"guild_id": guild_id, "user_id": user_id}
        result = await self._get_request("get_user_voice_state", params)
        return result.get("voice_state")
    
    # Voice connection methods
    async def join_voice_channel(self, guild_id, channel_id):
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "preserve_queue": True
        }
        return await self._post_request("join", data)
    
    async def disconnect_voice_channel(self, guild_id, user_id, preserve_queue=False):
        data = {
            "guild_id": guild_id,
            "user_id": user_id,
            "preserve_queue": preserve_queue
        }
        return await self._post_request("disconnect", data)
    
    # Queue management methods
    async def add_to_queue(self, guild_id, channel_id, video_id, video_title):
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "video_id": video_id,
            "video_title": video_title
        }
        return await self._post_request("add_to_queue", data)
    
    async def get_queue(self, guild_id, channel_id=None):
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
    
    # Playback control methods
    async def skip_track(self, guild_id, channel_id):
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id
        }
        return await self._post_request("skip", data)
    
    async def pause_playback(self, guild_id, channel_id):
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id
        }
        return await self._post_request("pause", data)
    
    async def resume_playback(self, guild_id, channel_id):
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id
        }
        return await self._post_request("resume", data)
    
    async def clear_queue(self, guild_id):
        data = {
            "guild_id": guild_id
        }
        return await self._post_request("clear_queue", data)
    
    async def shuffle_queue(self, guild_id, channel_id):
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id
        }
        return await self._post_request("shuffle_queue", data)
    
    async def add_multiple_to_queue(self, guild_id, channel_id, videos):
        # Track overall success
        overall_success = True
        added_count = 0
        error_messages = []
        
        # Add each video individually since the bot API doesn't support batch adds yet
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
    
    async def reorder_queue(self, guild_id, channel_id, old_index, new_index):
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "old_index": old_index,
            "new_index": new_index
        }
        return await self._post_request("reorder_queue", data)

    async def close(self):
        """Close the session when done"""
        if self.session:
            await self.session.close()
            self.session = None