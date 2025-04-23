"""
Add a track to the queue
"""
from .post_request import post_request

async def add_to_queue(base_url, secret_key, session, guild_id, channel_id, video_id, video_title):
    data = {
        "guild_id": guild_id,
        "channel_id": channel_id,
        "video_id": video_id,
        "video_title": video_title
    }
    return await post_request(base_url, secret_key, session, "add_to_queue", data)