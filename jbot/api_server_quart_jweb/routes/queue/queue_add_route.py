"""
Updated queue_add_route.py with search context preservation
"""
from quart import redirect, url_for, flash, request, current_app, render_template
from ...routes.auth.login_required import login_required
from ...validators import validate_add_to_queue, validate_add_multiple
from ...services import get_queue_and_bot_state, get_user_voice_channel, get_voice_channels

@login_required
async def queue_add_route(guild_id):
    """
    Handle adding videos to the queue with search context preservation
    
    Args:
        guild_id (str): Discord guild ID
        
    Returns:
        Response: Redirect to appropriate page with preserved context
    """
    
    # Get form data
    form = await request.form
    
    # Validate form data
    is_valid, errors = await validate_add_to_queue(form)
    if not is_valid:
        for error in errors:
            await flash(error, "error")
        return redirect(url_for('dashboard.server_dashboard_route', guild_id=guild_id))
    
    # Get validated data
    channel_id = form.get('channel_id')
    video_id = form.get('video_id')
    video_title = form.get('video_title', 'Unknown video')
    
    # Capture search context parameters for preservation
    search_context = {
        'query': form.get('query'),
        'search_type': form.get('search_type', 'comprehensive'),
        'playlist_id': form.get('playlist_id'),
        'page_token': form.get('page_token'),
        'prev_page_token': form.get('prev_page_token'),
        'page': form.get('page')
    }
    
    try:
        # Check 1: Is the user in a voice channel?
        user = await current_app.discord_oauth.fetch_user()
        user_id = str(user.id)
        user_voice_state = await current_app.discord_api_client.get_user_voice_state(guild_id, user_id)
        
        if not user_voice_state or not user_voice_state.get('channel_id'):
            await flash("You need to join a voice channel before adding music", "warning")
            return redirect_with_context(guild_id, search_context)
        
        # Check 2: Get the current queue to see if the bot is connected
        queue_info = await current_app.discord_api_client.get_queue(guild_id, channel_id)
        
        # If bot is not connected to the channel, tell user to use Discord command
        if not queue_info.get('is_connected', False):
            await flash("Bot is not connected to your voice channel. Type 'jbot' in a Discord text channel first to connect the bot.", "warning")
            return redirect_with_context(guild_id, search_context)
        
        # Check 3: Make sure bot and user are in the same channel
        if user_voice_state.get('channel_id') != channel_id:
            await flash("You must be in the same voice channel as the bot to add music", "warning")
            return redirect_with_context(guild_id, search_context)
        
        # Now add to queue using the Discord bot API
        result = await current_app.discord_api_client.add_to_queue(guild_id, channel_id, video_id, video_title)
        
        if result.get('success'):
            await flash(f"Added '{video_title}' to queue", "success")
        else:
            await flash(f"Error adding to queue: {result.get('error', 'Unknown error')}", "error")
            
    except Exception as e:
        await flash(f"Error adding to queue: {str(e)}", "error")
    
    # Always redirect back with preserved search context
    return redirect_with_context(guild_id, search_context)


def redirect_with_context(guild_id, search_context):
    """
    Helper function to redirect with preserved search context
    
    Args:
        guild_id (str): Discord guild ID
        search_context (dict): Search context parameters
        
    Returns:
        Response: Redirect response with context preserved
    """
    # Build redirect parameters, excluding None/empty values
    redirect_params = {'guild_id': guild_id}
    
    for key, value in search_context.items():
        if value:  # Only include non-empty values
            redirect_params[key] = value
    
    # Determine the appropriate redirect target
    if search_context.get('playlist_id') or search_context.get('query'):
        # Redirect to search page with context
        return redirect(url_for('search.youtube_search_route', **redirect_params))
    else:
        # Redirect to server dashboard with channel selection
        if search_context.get('channel_id'):
            redirect_params['channel_id'] = search_context['channel_id']
        return redirect(url_for('dashboard.server_dashboard_route', **redirect_params))


# Alternative implementation using decorators for cleaner code
def preserve_search_context(func):
    """
    Decorator to automatically preserve search context in queue operations
    """
    async def wrapper(guild_id):
        form = await request.form
        
        # Extract search context
        context = {
            'query': form.get('query'),
            'search_type': form.get('search_type'),
            'playlist_id': form.get('playlist_id'),
            'page_token': form.get('page_token'),
            'prev_page_token': form.get('prev_page_token'),
            'page': form.get('page'),
            'channel_id': form.get('channel_id')
        }
        
        try:
            # Call the original function
            result = await func(guild_id)
            
            # If it's a redirect, preserve context
            if hasattr(result, 'location'):
                return redirect_with_context(guild_id, context)
            
            return result
            
        except Exception as e:
            # On error, still preserve context
            await flash(f"Error: {str(e)}", "error")
            return redirect_with_context(guild_id, context)
    
    return wrapper


# Updated multiple add route with context preservation
@login_required
@preserve_search_context
async def queue_add_multiple_route_with_context(guild_id):
    """
    Handle adding multiple videos with automatic context preservation
    """
    form = await request.form
    
    # Validate form data and extract videos
    is_valid, errors, videos = await validate_add_multiple(form)
    
    # Get parameters that need to be kept even if validation fails
    channel_id = form.get('channel_id')
    
    if not is_valid:
        for error in errors:
            await flash(error, "error")
        return  # Will be handled by decorator
    
    # Verification and processing logic...
    user = await current_app.discord_oauth.fetch_user()
    user_id = str(user.id)
    user_voice_state = await current_app.discord_api_client.get_user_voice_state(guild_id, user_id)
    
    if not user_voice_state or not user_voice_state.get('channel_id'):
        await flash("You must join a voice channel before adding music to the queue", "warning")
        return
    
    queue_info = await current_app.discord_api_client.get_queue(guild_id, channel_id)
    if not queue_info.get('is_connected', False):
        await flash("Bot is not connected to your voice channel. Type 'jbot' in a Discord text channel first to connect the bot.", "warning")
        return
    
    if user_voice_state.get('channel_id') != channel_id:
        await flash("You must be in the same voice channel as the bot to add music", "warning")
        return
    
    # Enforce 50 track limit
    if len(videos) > 50:
        videos = videos[:50]
        await flash("Limited to adding 50 videos at once", "warning")
    
    # Add videos to queue
    try:
        result = await current_app.discord_api_client.add_multiple_to_queue(guild_id, channel_id, videos)
        
        if result.get('success'):
            await flash(f"Added {result.get('added_count', 0)} videos to queue", "success")
        else:
            await flash(f"Error adding videos to queue: {result.get('error', 'Unknown error')}", "error")
    except Exception as e:
        await flash(f"Error adding videos to queue: {str(e)}", "error")


# Enhanced search route that maintains state better
@login_required
async def youtube_search_route_enhanced(guild_id):
    """
    Enhanced search route that better preserves state and context
    """
    youtube_client = current_app.youtube_client
    
    # Get user's voice channel
    user = await current_app.discord_oauth.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Get voice channels
    voice_channels = await get_voice_channels(guild_id)
    
    # Get guild info
    user_guilds = await current_app.discord_oauth.fetch_guilds()
    guild_info = next((g for g in user_guilds if str(g.id) == guild_id), None)
    
    # Initialize context with preserved values
    selected_channel_id = request.args.get('channel_id') or (user_voice_channel['id'] if user_voice_channel else None)
    
    # Initialize all template variables
    template_context = {
        'guild_id': guild_id,
        'guild_name': getattr(guild_info, 'name', f"Server {guild_id}"),
        'guild_icon': getattr(guild_info, 'icon', None),
        'voice_channels': voice_channels,
        'user_voice_channel': user_voice_channel,
        'selected_channel_id': selected_channel_id,
        'search_results': [],
        'playlist_results': [],
        'playlist_videos': [],
        'playlist_details': None,
        'selected_playlist_id': None,
        'page_token': None,
        'next_page_token': None,
        'prev_page_token': None,
        'current_page': 1,
        'total_pages': 1,
        'total_results': 0,
        'has_next_page': False,
        'has_prev_page': False,
        'preserved_query': request.args.get('query', ''),
        'preserved_search_type': request.args.get('search_type', 'comprehensive')
    }
    
    # Process search/playlist logic here...
    # [Previous search logic would go here with context preservation]
    
    # Get queue for selected channel
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, selected_channel_id)
    template_context.update({
        'queue': queue_info.get("queue", []),
        'current_track': queue_info.get("current_track"),
        'bot_state': bot_state
    })
    
    return await render_template('servers_dashboard.html', **template_context)