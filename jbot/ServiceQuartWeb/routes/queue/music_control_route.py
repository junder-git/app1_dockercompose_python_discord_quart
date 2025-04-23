"""
Music control route for pause, play, skip commands
"""
from quart import request, jsonify, current_app
from ...routes.auth import login_required, get_queue_and_bot_state

@login_required
async def music_control_route(guild_id):
    """
    Handle music control commands (play, pause, skip, etc.)
    
    Args:
        guild_id (str): The Discord guild ID
        
    Returns:
        Response: JSON result of the command
    """
    discord_client = current_app.discord_client
    form = await request.form
    channel_id = form.get('channel_id')
    command = form.get('command')

    # Get queue and bot state
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, channel_id)
    if not bot_state.get('is_connected'):
        return jsonify({"error": "Bot is not connected to the voice channel"}), 400

    # Execute the command
    if command == "pause":
        await discord_client.pause(guild_id, channel_id)
    elif command == "resume":
        await discord_client.resume(guild_id, channel_id)
    elif command == "skip":
        await discord_client.skip(guild_id, channel_id)
    else:
        return jsonify({"error": "Invalid command"}), 400

    return jsonify({"success": True})