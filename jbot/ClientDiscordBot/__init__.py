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
    
    async def add_multiple_to_queue(base_url, secret_key, session, guild_id, channel_id, videos):
        overall_success = True
        added_count = 0
        error_messages = []

        for video in videos:
            video_id = video.get('id')
            video_title = video.get('title', 'Unknown Video')

            result = await add_to_queue(base_url, secret_key, session, guild_id, channel_id, video_id, video_title)

            if result.get('success'):
                added_count += 1
            else:
                overall_success = False
                error_messages.append(f"Error adding '{video_title}': {result.get('error')}")

        return {
            "success": overall_success or added_count > 0,
            "added_count": added_count,
            "total_count": len(videos),
            "message": f"Added {added_count} of {len(videos)} videos to queue",
            "errors": error_messages if error_messages else None
        }
    
    async def add_to_queue(base_url, secret_key, session, guild_id, channel_id, video_id, video_title):
        data = {
            "guild_id": guild_id,
            "channel_id": channel_id,
            "video_id": video_id,
            "video_title": video_title
        }
        return await post_request(base_url, secret_key, session, "add_to_queue", data)
    async def clear_queue(base_url, secret_key, session, guild_id, channel_id=None):
        data = {"guild_id": guild_id}
        if channel_id:
            data["channel_id"] = channel_id
        return await post_request(base_url, secret_key, session, "clear_queue", data)
    async def close_session(session):
        if session:
            await session.close()
            return None
        return session
    async def ensure_session(session):
        if session is None:
            return aiohttp.ClientSession()
        return session
    async def get_guild_count(base_url, secret_key, session):
        result = await get_request(base_url, secret_key, session, "guild_count")
        return result.get("count", 0)   
    async def get_guild_ids(base_url, secret_key, session):
        result = await get_request(base_url, secret_key, session, "guild_ids")
        return result.get("guild_ids", []) 
    def default_queue_response():
        return {
            "queue": [],
            "current_track": None,
            "is_connected": False,
            "is_playing": False,
            "is_paused": False
        }

    async def get_queue(base_url, secret_key, session, guild_id, channel_id=None):
        params = {"guild_id": guild_id}
        if channel_id:
            params["channel_id"] = channel_id

        result = await get_request(base_url, secret_key, session, "get_queue", params, default_queue_response())

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
    async def get_request(base_url, secret_key, session, endpoint, params=None, default_response=None):
        try:
            session = await ensure_session(session)
            headers = {"Authorization": f"Bearer {secret_key}"}
            url = f"{base_url}/{endpoint}"
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return default_response or {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API ({endpoint}): {e}")
            return default_response or {"success": False, "error": str(e)}
    async def post_request(base_url, secret_key, session, endpoint, data):
        try:
            session = await ensure_session(session)
            headers = {"Authorization": f"Bearer {secret_key}"}
            url = f"{base_url}/{endpoint}"
            async with session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API ({endpoint}): {e}")
            return {"success": False, "error": str(e)}
    async def public_get(base_url, secret_key, session, endpoint, params=None):
        session = await ensure_session(session)
        headers = {"Authorization": f"Bearer {secret_key}"}

        if '?' in endpoint and params:
            query_string = urlencode(params)
            url = f"{base_url}{endpoint}&{query_string}"
        elif params:
            query_string = urlencode(params)
            url = f"{base_url}{endpoint}?{query_string}"
        else:
            url = f"{base_url}{endpoint}"

        return await session.get(url, headers=headers)
    async def public_post(base_url, secret_key, session, endpoint, data=None):
        session = await ensure_session(session)
        headers = {"Authorization": f"Bearer {secret_key}"}
        url = f"{base_url}{endpoint}"
        return await session.post(url, headers=headers, json=data)
__all__ = [
    'DiscordAPIClient'
]