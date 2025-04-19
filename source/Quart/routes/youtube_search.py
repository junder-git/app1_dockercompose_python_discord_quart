"""
YouTube search route for JBot Quart application
"""
from quart import Blueprint, render_template, redirect, url_for, request, flash
from .helpers import login_required, get_voice_channels, get_user_voice_channel, get_queue_and_bot_state
from forms import SearchForm

# Create a blueprint for YouTube search route
youtube_search_bp = Blueprint('youtube_search', __name__)

@youtube_search_bp.route('/server/<guild_id>/search', methods=['GET', 'POST'])
@login_required
async def youtube_search_route(guild_id):
    """Handle YouTube search requests for videos, playlists, and artists with pagination"""
    # Import from current app context
    from quart import current_app
    discord = current_app.discord
    bot_api = current_app.bot_api
    youtube_service = current_app.youtube_service
    
    search_results = []
    playlist_results = []
    artist_results = []
    playlist_videos = []
    selected_playlist_id = None
    playlist_details = None
    search_type = request.args.get('search_type', 'video')
    
    # Pagination parameters
    page_token = request.args.get('page_token')
    current_page = int(request.args.get('page', 1))
    next_page_token = None
    prev_page_token = request.args.get('prev_page_token')
    total_results = 0
    
    # Get guild info for template
    user_guilds = await discord.fetch_guilds()
    guild_info = next((g for g in user_guilds if str(g.id) == guild_id), None)
    if not guild_info:
        return redirect(url_for('dashboard.dashboard_route'))
    
    # Get all voice channels
    all_voice_channels = await get_voice_channels(guild_id)
    
    # Get user's voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id, bot_api)
    
    # Create search form
    form = await SearchForm.create_form()
    
    # Check if a playlist ID was provided
    selected_playlist_id = request.args.get('playlist_id')
    if selected_playlist_id:
        # Get playlist details using the YouTube service
        playlist_details = await youtube_service.get_playlist_details(selected_playlist_id)
        total_results = playlist_details.get('video_count', 0)
        
        # Get playlist videos with pagination
        playlist_videos, next_page_token, video_count = await youtube_service.get_playlist_videos(
            selected_playlist_id, page_token)
        
        # If we didn't get a video count from the playlist details, use what we got from the videos API
        if total_results == 0:
            total_results = video_count
    
    # Handle form submission - only process if user is in a voice channel
    if form.validate_on_submit() and user_voice_channel:
        query = form.query.data
        search_type = form.search_type.data
        
        if query:
            # Check if the query is a YouTube URL
            video_id = youtube_service.extract_video_id(query)
            playlist_id = youtube_service.extract_playlist_id(query)
            
            if video_id:
                # If it's a video URL, get the video details and redirect to add to queue
                video_details = await youtube_service.get_video_details(video_id)
                video_title = video_details.get('title', 'Unknown Video')
                
                # Add to queue and redirect
                result = await bot_api.add_to_queue(guild_id, user_voice_channel['id'], video_id, video_title)
                if result.get('success'):
                    flash(f"Added '{video_title}' to queue", "success")
                else:
                    flash(f"Error adding to queue: {result.get('error')}", "error")
                
                return redirect(url_for('server_dashboard.server_dashboard_route', guild_id=guild_id))
                
            elif playlist_id:
                # If it's a playlist URL, redirect to the playlist view
                return redirect(url_for('youtube_search.youtube_search_route', guild_id=guild_id, playlist_id=playlist_id))
                
            else:
                # Regular search based on search type
                if search_type == 'video':
                    search_results = await youtube_service.search_videos(query)
                elif search_type == 'playlist':
                    playlist_results = await youtube_service.search_playlists(query)
                elif search_type == 'artist':
                    artist_results = await youtube_service.search_artists(query)
                elif search_type == 'both':
                    search_results = await youtube_service.search_videos(query, max_results=5)
                    playlist_results = await youtube_service.search_playlists(query, max_results=5)
                elif search_type == 'comprehensive':
                    search_results = await youtube_service.search_videos(query, max_results=5)
                    playlist_results = await youtube_service.search_playlists(query, max_results=5)
                    artist_results = await youtube_service.search_artists(query, max_results=5)
    elif request.method == 'POST' and not user_voice_channel:
        flash("You must join a voice channel in Discord before searching for music", "warning")
    
    # If the form wasn't submitted via POST, pre-populate from request args
    elif request.method == 'GET' and 'query' in request.args:
        form.query.data = request.args.get('query')
        form.search_type.data = request.args.get('search_type', 'comprehensive')
    
    # Always use the user's current voice channel as the selected channel
    selected_channel_id = user_voice_channel['id'] if user_voice_channel else None
    if selected_channel_id and form.channel_id:
        form.channel_id.data = selected_channel_id
    
    # Get queue for the selected channel (if user is in a voice channel)
    queue_info = {"queue": [], "current_track": None}
    bot_state = {
        'connected': False,
        'is_playing': False,
        'voice_channel_id': None,
        'voice_channel_name': None
    }
    
    if selected_channel_id:
        queue_info, bot_state = await get_queue_and_bot_state(guild_id, selected_channel_id, all_voice_channels, bot_api)
    
    # Calculate pagination information
    max_results = 50  # YouTube API default
    total_pages = (total_results + max_results - 1) // max_results if total_results > 0 else 1
    has_next_page = next_page_token is not None
    has_prev_page = current_page > 1
    
    # Safe attribute access
    guild_icon = getattr(guild_info, 'icon', None)
    guild_name = getattr(guild_info, 'name', f"Server {guild_id}")
    
    return await render_template(
        'server_dashboard.html',
        guild_id=guild_id,
        guild_name=guild_name,
        guild_icon=guild_icon,
        voice_channels=all_voice_channels,
        search_results=search_results,
        playlist_results=playlist_results,
        artist_results=artist_results,
        playlist_videos=playlist_videos,
        playlist_details=playlist_details,
        selected_playlist_id=selected_playlist_id,
        selected_channel_id=selected_channel_id,
        user_voice_channel=user_voice_channel,
        queue=queue_info.get("queue", []),
        current_track=queue_info.get("current_track"),
        bot_state=bot_state,
        search_type=search_type,
        # Add form to the template
        form=form,
        # Pagination data
        current_page=current_page,
        total_pages=total_pages,
        next_page_token=next_page_token,
        prev_page_token=prev_page_token,
        page_token=page_token,
        has_next_page=has_next_page,
        has_prev_page=has_prev_page,
        total_results=total_results
    )