"""
Discord API Blueprint for Quart
"""
from quart import Blueprint, request, current_app

# Create the blueprint
discord_api_blueprint = Blueprint('discord_api', __name__, url_prefix='/api/discord')

@discord_api_blueprint.route('/queue/<guild_id>')
async def get_queue_route(guild_id):
    """Get the queue for a guild"""
    bot_api = current_app.discord_client
    channel_id = request.args.get('channel_id')
    
    result = await bot_api.get_queue(guild_id, channel_id)
    return result

@discord_api_blueprint.route('/queue/add', methods=['POST'])
async def add_to_queue_route():
    """Add a track to the queue"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    video_id = data.get('video_id')
    video_title = data.get('video_title')
    
    if not all([guild_id, channel_id, video_id, video_title]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
    return result

@discord_api_blueprint.route('/queue/add_multiple', methods=['POST'])
async def add_multiple_to_queue_route():
    """Add multiple tracks to the queue"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    videos = data.get('videos', [])
    
    if not all([guild_id, channel_id, videos]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.add_multiple_to_queue(guild_id, channel_id, videos)
    return result

@discord_api_blueprint.route('/queue/clear', methods=['POST'])
async def clear_queue_route():
    """Clear the queue for a guild"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    
    if not guild_id:
        return {"success": False, "error": "Missing guild_id"}, 400
    
    result = await bot_api.clear_queue(guild_id, channel_id)
    return result

@discord_api_blueprint.route('/queue/shuffle', methods=['POST'])
async def shuffle_queue_route():
    """Shuffle the queue for a guild"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    
    if not all([guild_id, channel_id]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.shuffle_queue(guild_id, channel_id)
    return result

@discord_api_blueprint.route('/queue/reorder', methods=['POST'])
async def reorder_queue_route():
    """Reorder an item in the queue"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    old_index = data.get('old_index')
    new_index = data.get('new_index')
    
    if not all([guild_id, channel_id, old_index is not None, new_index is not None]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.reorder_queue(guild_id, channel_id, old_index, new_index)
    return result

@discord_api_blueprint.route('/playback/skip', methods=['POST'])
async def skip_track_route():
    """Skip the current track"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    
    if not all([guild_id, channel_id]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.skip_track(guild_id, channel_id)
    return result

@discord_api_blueprint.route('/playback/pause', methods=['POST'])
async def pause_playback_route():
    """Pause the current playback"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    
    if not all([guild_id, channel_id]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.pause_playback(guild_id, channel_id)
    return result

@discord_api_blueprint.route('/playback/resume', methods=['POST'])
async def resume_playback_route():
    """Resume the current playback"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    
    if not all([guild_id, channel_id]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.resume_playback(guild_id, channel_id)
    return result

@discord_api_blueprint.route('/voice/join', methods=['POST'])
async def join_voice_channel_route():
    """Join a voice channel"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    channel_id = data.get('channel_id')
    
    if not all([guild_id, channel_id]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.join_voice_channel(guild_id, channel_id)
    return result

@discord_api_blueprint.route('/voice/disconnect', methods=['POST'])
async def disconnect_voice_channel_route():
    """Disconnect from a voice channel"""
    bot_api = current_app.discord_client
    data = await request.get_json()
    
    guild_id = data.get('guild_id')
    user_id = data.get('user_id')
    preserve_queue = data.get('preserve_queue', False)
    
    if not all([guild_id, user_id]):
        return {"success": False, "error": "Missing required fields"}, 400
    
    result = await bot_api.disconnect_voice_channel(guild_id, user_id, preserve_queue)
    return result

@discord_api_blueprint.route('/user/voice_state')
async def get_user_voice_state_route():
    """Get the voice state of a user"""
    bot_api = current_app.discord_client
    
    guild_id = request.args.get('guild_id')
    user_id = request.args.get('user_id')
    
    if not all([guild_id, user_id]):
        return {"success": False, "error": "Missing required parameters"}, 400
    
    result = await bot_api.get_user_voice_state(guild_id, user_id)
    return {"voice_state": result}

@discord_api_blueprint.route('/guilds/count')
async def get_guild_count_route():
    """Get the count of guilds the bot is in"""
    bot_api = current_app.discord_client
    count = await bot_api.get_guild_count()
    return {"count": count}

@discord_api_blueprint.route('/guilds/ids')
async def get_guild_ids_route():
    """Get the IDs of all guilds the bot is in"""
    bot_api = current_app.discord_client
    guild_ids = await bot_api.get_guild_ids()
    return {"guild_ids": guild_ids}