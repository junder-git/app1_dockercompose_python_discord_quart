"""
Playlist confirmation route for JBot Quart application
"""
from quart import Blueprint, render_template, redirect, url_for, request, flash, current_app
from .helpers import login_required, get_voice_channels, get_user_voice_channel

# Create a blueprint for playlist confirmation route
playlist_confirmation_bp = Blueprint('playlist_confirmation', __name__)

@playlist_confirmation_bp.route('/server/<guild_id>/playlist_confirmation')
@login_required
async def playlist_confirmation_route(guild_id):
    """Confirmation page for adding YouTube playlists"""
    discord = current_app.discord
    bot_api = current_app.bot_api
    youtube_service = current_app.youtube_service
    
    playlist_id = request.args.get('playlist_id')
    channel_id = request.args.get('channel_id')
    
    if not playlist_id or not channel_id:
        flash("Missing playlist ID or channel ID", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
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
    user_voice_channel = await get_user_voice_channel(guild_id, user_id, bot_api)
    
    # Get playlist details using the YouTube service
    playlist_details = await youtube_service.get_playlist_details(playlist_id)
    
    # Get first page of videos
    videos, next_page_token, total_results = await youtube_service.get_playlist_videos(playlist_id)
    
    # Safe attribute access
    guild_icon = getattr(guild_info, 'icon', None)
    guild_name = getattr(guild_info, 'name', f"Server {guild_id}")
    
    max_results = 50  # YouTube API default
    total_pages = (total_results + max_results - 1) // max_results if total_results > 0 else 1
    
    return await render_template(
        'playlist_confirmation.html',
        guild_id=guild_id,
        guild_name=guild_name,
        guild_icon=guild_icon,
        playlist_id=playlist_id,
        playlist_details=playlist_details,
        videos=videos,
        channel_id=channel_id,
        total_results=total_results,
        total_pages=total_pages,
        user_voice_channel=user_voice_channel
    )