"""
Server dashboard route for JBot Quart application
"""
from quart import Blueprint, render_template, redirect, url_for, request
from .helpers import login_required, get_voice_channels, get_user_voice_channel, get_queue_and_bot_state
from forms import SearchForm, MusicControlForm, ShuffleQueueForm, PlaylistForm, AddMultipleForm

# Create a blueprint for server dashboard route
server_dashboard_bp = Blueprint('server_dashboard', __name__)

@server_dashboard_bp.route('/server/<guild_id>/dashboard')
@login_required
async def server_dashboard_route(guild_id):
    """Server dashboard for viewing voice channels and music status"""
    # Import from current app context
    from quart import current_app
    discord = current_app.discord
    bot_api = current_app.bot_api
    
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
    
    # Get current selected channel (if any)
    selected_channel_id = request.args.get('channel_id', None)
    
    # If no channel is selected but user is in a voice channel, use that
    if not selected_channel_id and user_voice_channel:
        selected_channel_id = user_voice_channel['id']
    
    # Get queue for selected channel (if applicable)
    queue_info, bot_state = await get_queue_and_bot_state(
        guild_id, selected_channel_id, voice_channels, bot_api
    )
    
    # Initialize all forms
    music_control_form = MusicControlForm()
    search_form = SearchForm()
    shuffle_queue_form = ShuffleQueueForm()
    playlist_form = PlaylistForm()
    add_multiple_form = AddMultipleForm()
    
    # Set default values    
    if selected_channel_id != None:
        music_control_form.channel_id.data = selected_channel_id
        search_form.channel_id.data = selected_channel_id
        shuffle_queue_form.channel_id.data = selected_channel_id
        playlist_form.channel_id.data = selected_channel_id
        add_multiple_form.channel_id.data = selected_channel_id
    
    # Safe attribute access
    guild_icon = getattr(guild_info, 'icon', None)
    guild_name = getattr(guild_info, 'name', f"Server {guild_id}")
    
    return await render_template(
        'server_dashboard.html',
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
        # Forms
        music_control_form=music_control_form,
        search_form=search_form,
        shuffle_queue_form=shuffle_queue_form,
        playlist_form=playlist_form,
        add_multiple_form=add_multiple_form
    )