"""
Server dashboard route
"""
from quart import render_template, redirect, url_for, request, current_app
from ...auth.login_required import login_required
from ...services import get_voice_channels, get_user_voice_channel, get_queue_and_bot_state
from ...validators import validate_guild_id, validate_channel_id, generate_csrf_token

@login_required
async def server_dashboard_route(guild_id):
    """
    Server dashboard for viewing voice channels and music status
    
    Args:
        guild_id (str): The Discord guild ID
        
    Returns:
        Response: Rendered server dashboard or redirect to main dashboard
    """
    # Validate guild ID
    if not validate_guild_id(guild_id):
        return redirect(url_for('dashboard.dashboard_route'))
    
    discord = current_app.discord
    
    # Get guild info
    user_guilds = await discord.fetch_guilds()
    guild_info = next((g for g in user_guilds if str(g.id) == guild_id), None)
    
    if not guild_info:
        return redirect(url_for('dashboard.dashboard_route'))
    
    # Get voice channels
    voice_channels = await get_voice_channels(guild_id)
    
    # Get user's voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Get current selected channel (if any)
    selected_channel_id = request.args.get('channel_id', None)
    
    # If no channel is selected but user is in a voice channel, use that
    if not selected_channel_id and user_voice_channel:
        selected_channel_id = user_voice_channel['id']
    
    # Validate selected channel ID 
    if selected_channel_id and not validate_channel_id(selected_channel_id, voice_channels):
        selected_channel_id = None
    
    # Get queue for selected channel (if applicable)
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, selected_channel_id)
    
    # Generate CSRF token
    csrf_token = generate_csrf_token()
    
    # Safe attribute access
    guild_icon = getattr(guild_info, 'icon', None)
    guild_name = getattr(guild_info, 'name', f"Server {guild_id}")
    
    return await render_template(
        'servers_dashboard.html',
        guild_id=guild_id,
        guild_name=guild_name,
        guild_icon=guild_icon,
        voice_channels=voice_channels,
        search_results=[],  # Empty initially, use search route for results
        selected_channel_id=selected_channel_id,
        user_voice_channel=user_voice_channel,
        queue=queue_info.get("queue", []),
        current_track=queue_info.get("current_track"),
        bot_state=bot_state,
        csrf_token=csrf_token
    )