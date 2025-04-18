"""
AJAX queue data route for JBot Quart application
"""
from quart import Blueprint, request
from .helpers import login_required, get_voice_channels, get_queue_and_bot_state

# Create a blueprint for queue AJAX route
queue_ajax_bp = Blueprint('queue_ajax', __name__)

@queue_ajax_bp.route('/server/<guild_id>/queue/ajax')
@login_required
async def queue_ajax_route(guild_id):
    """AJAX endpoint to retrieve queue data for real-time updates"""
    # Import from current app context
    from quart import current_app
    bot_api = current_app.bot_api
    
    # Get the channel ID from query parameters
    channel_id = request.args.get('channel_id')
    
    # Get voice channels to get the channel name
    voice_channels = await get_voice_channels(guild_id)
    
    # Get queue info and bot state
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, channel_id, voice_channels, bot_api)
    
    # Return the queue information in JSON format
    return {
        "queue": queue_info.get("queue", []),
        "current_track": queue_info.get("current_track"),
        "is_connected": bot_state.get("connected", False),
        "is_playing": bot_state.get("is_playing", False),
        "is_paused": queue_info.get("is_paused", False)
    }