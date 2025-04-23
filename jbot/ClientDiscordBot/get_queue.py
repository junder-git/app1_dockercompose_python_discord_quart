"""
Get the current queue for a guild
"""
from .get_request import get_request

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