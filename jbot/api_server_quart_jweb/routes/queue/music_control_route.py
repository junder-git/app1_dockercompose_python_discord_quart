"""
Music control route for pause, play, skip commands
"""
from quart import request, jsonify, current_app
from ...routes.auth.login_required import login_required
from ...services import get_queue_and_bot_state

@login_required
async def music_control_route(guild_id):
    """
    Handle music control commands (play, pause, skip, etc.)
    """
    # Debug info
    form = await request.form
    print(f"Music control form data: {form}")
    
    channel_id = form.get('channel_id')
    command = form.get('command')
    
    if not channel_id:
        print("Missing channel ID in music control")
        return jsonify({"error": "Missing channel ID"}), 400
    
    # Debug the queue and bot state
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, channel_id)
    print(f"Queue info: {queue_info}")
    print(f"Bot state: {bot_state}")
    
    # Check if bot is connected
    if not bot_state.get('connected'):
        message = "Bot is not connected to the voice channel"
        print(message)
        return jsonify({"error": message}), 400
    
    # Execute command
    try:
        if command == "pause":
            result = await current_app.discord_api_client.pause_playback(guild_id, channel_id)
        elif command == "resume":
            result = await current_app.discord_api_client.resume_playback(guild_id, channel_id)
        elif command == "skip":
            result = await current_app.discord_api_client.skip_track(guild_id, channel_id)
        else:
            return jsonify({"error": "Invalid command"}), 400
        
        print(f"Command result: {result}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"Error executing command: {e}")
        return jsonify({"error": str(e)}), 500