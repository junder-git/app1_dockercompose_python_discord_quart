"""
Clear the queue for a guild
"""
from .post_request import post_request

async def clear_queue(base_url, secret_key, session, guild_id, channel_id=None):
    data = {"guild_id": guild_id}
    if channel_id:
        data["channel_id"] = channel_id
    return await post_request(base_url, secret_key, session, "clear_queue", data)