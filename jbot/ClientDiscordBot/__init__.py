"""
Discord API Client - Blueprint for Discord bot communication
"""
import aiohttp
from urllib.parse import urlencode
# Define the DiscordAPIClient class
class DiscordAPIClient:
    def __init__(self, host, port, secret_key):
        self.base_url = f"http://{host}:{port}/api"
        self.secret_key = secret_key
        self.session = None
        self.guild_id = None
        self.channel_id = None
        self.videos = []
    
    async def add_multiple_to_queue(self):
        overall_success = True
        added_count = 0
        error_messages = []

        for self.video in self.videos:
            video_id = self.video.get('id')
            video_title = self.video.get('title', 'Unknown Video')

            result = await self.add_to_queue(self, video_id, video_title)

            if result.get('success'):
                added_count += 1
            else:
                overall_success = False
                error_messages.append(f"Error adding '{video_title}': {result.get('error')}")

        return {
            "success": overall_success or added_count > 0,
            "added_count": added_count,
            "total_count": len(self.videos),
            "message": f"Added {added_count} of {len(self.videos)} videos to queue",
            "errors": error_messages if error_messages else None
        }
    
    async def add_to_queue(self, video_id, video_title):
        data = {
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "video_id": video_id,
            "video_title": video_title
        }
        return await self.post_request(self, "add_to_queue", data)
    async def clear_queue(self):
        data = {"guild_id": self.guild_id}
        if self.channel_id:
            data["channel_id"] = self.channel_id
        return await self.post_request(self, "clear_queue", data)
    async def close_session(self):
        if self.session:
            await self.session.close()
            return None
        return self.session
    async def ensure_session(self):
        if self.session is None:
            return aiohttp.ClientSession()
        return self.session
    async def get_guild_count(self):
        result = await self.get_request(self, "guild_count")
        return result.get("count", 0)   
    async def get_guild_ids(self):
        result = await self.get_request(self, "guild_ids")
        return result.get("guild_ids", []) 
    def default_queue_response():
        return {
            "queue": [],
            "current_track": None,
            "is_connected": False,
            "is_playing": False,
            "is_paused": False
        }

    async def get_queue(self):
        params = {"guild_id": self.guild_id}
        if self.channel_id:
            params["channel_id"] = self.channel_id

        result = await self.get_request(self, "get_queue", params, self.default_queue_response())

        if "queue" not in result:
            result["queue"] = []
        if "current_track" not in result:
            result["current_track"] = None
        if "is_connected" not in result:
            result["is_connected"] = result.get("current_track") is not None
        if "is_playing" not in result:
            result["is_playing"] = result.get("current_track") is not None
        if "is_paused" not in result:
            result["is_paused"] = False

        return result
    async def get_request(self, endpoint, params=None, default_response=None):
        try:
            self.session = await self.ensure_session(self.session)
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
    async def post_request(self, endpoint, data):
        try:
            self.session = await self.ensure_session(self.session)
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
    async def public_get(self, endpoint, params=None):
        self.session = await self.ensure_session(self.session)
        headers = {"Authorization": f"Bearer {self.secret_key}"}

        if '?' in endpoint and params:
            query_string = urlencode(params)
            url = f"{self.base_url}{endpoint}&{query_string}"
        elif params:
            query_string = urlencode(params)
            url = f"{self.base_url}{endpoint}?{query_string}"
        else:
            url = f"{self.base_url}{endpoint}"

        return await self.session.get(url, headers=headers)
    async def public_post(self, endpoint, data=None):
        self.session = await self.ensure_session(self.session)
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        url = f"{self.base_url}{endpoint}"
        return await self.session.post(url, headers=headers, json=data)

__all__ = [
    'DiscordAPIClient'
]