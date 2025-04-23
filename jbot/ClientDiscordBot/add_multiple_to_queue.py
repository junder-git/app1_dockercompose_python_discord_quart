"""
Add multiple tracks to the queue
"""
from .add_to_queue import add_to_queue

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