"""
Music control route for JBot Quart application
"""
from quart import Blueprint, redirect, url_for, flash
from .helpers import login_required
from forms import MusicControlForm

# Create a blueprint for music control route
music_control_bp = Blueprint('music_control', __name__)

@music_control_bp.route('/server/<guild_id>/music/control', methods=['POST'])
@login_required
async def music_control_route(guild_id):
    """Handle music control commands: join, skip, pause, resume, stop"""
    # Import from current app context
    from quart import current_app
    discord = current_app.discord
    bot_api = current_app.bot_api
    
    # Create and validate form
    form = await MusicControlForm.create_form()
    
    if not form.validate_on_submit():
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error in {field}: {error}", "error")
        return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Get form data
    command = form.command.data
    channel_id = form.channel_id.data
    
    try:
        if command == 'join':
            result = await bot_api.join_voice_channel(guild_id, channel_id)
            if result.get('success'):
                flash("Bot joined voice channel", "success")
            else:
                flash(f"Error joining channel: {result.get('error')}", "error")
        elif command == 'skip':
            result = await bot_api.skip_track(guild_id, channel_id)
            if result.get('success'):
                flash("Skipped to next track", "success")
            else:
                flash(f"Error skipping track: {result.get('error')}", "error")
        elif command == 'pause':
            result = await bot_api.pause_playback(guild_id, channel_id)
            if result.get('success'):
                flash("Playback paused", "success")
            else:
                flash(f"Error pausing playback: {result.get('error')}", "error")
        elif command == 'resume':
            result = await bot_api.resume_playback(guild_id, channel_id)
            if result.get('success'):
                flash("Playback resumed", "success")
            else:
                flash(f"Error resuming playback: {result.get('error')}", "error")
        elif command == 'stop':
            # Get the user ID of the current user
            user = await discord.fetch_user()
            user_id = str(user.id)
            # Call the disconnect function with preserve_queue=False to clear the queue
            result = await bot_api.disconnect_voice_channel(guild_id, user_id, preserve_queue=False)
            if result.get('success'):
                flash("Stopped playback, cleared queue and disconnected bot", "success")
            else:
                flash(f"Error stopping playback: {result.get('error')}", "error")
        else:
            flash(f"Unknown command: {command}", "error")
    except Exception as e:
        flash(f"Error executing command: {str(e)}", "error")
    
    # Redirect back to dashboard with the selected channel
    return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id, channel_id=channel_id))