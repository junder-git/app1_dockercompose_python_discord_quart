"""
YouTube search route for JBot Quart application
"""
from quart import Blueprint, render_template, request, session, url_for
from .helpers import login_required, get_voice_channels, get_user_voice_channel
from forms import SearchForm, MusicControlForm, ShuffleQueueForm, PlaylistForm, AddMultipleForm, UrlForm

# Create a blueprint for YouTube search
youtube_search_bp = Blueprint('youtube_search', __name__)

@youtube_search_bp.route('/server/<guild_id>/search', methods=['GET', 'POST'])
@login_required
async def youtube_search_route(guild_id):
    """Search YouTube for videos or display playlist details"""
    # Import from current app context
    from quart import current_app
    discord = current_app.discord
    bot_api = current_app.bot_api
    
    # Get user's voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id, bot_api)
    
    # Get voice channels
    voice_channels = await get_voice_channels(guild_id)
    
    # Get guild info
    user_guilds = await discord.fetch_guilds()
    guild_info = next((g for g in user_guilds if str(g.id) == guild_id), None)
    
    # Safe attribute access
    guild_icon = getattr(guild_info, 'icon', None)
    guild_name = getattr(guild_info, 'name', f"Server {guild_id}")
    
    # Initialize forms
    search_form = SearchForm()
    music_control_form = MusicControlForm()
    shuffle_queue_form = ShuffleQueueForm()
    playlist_form = PlaylistForm()  # Add this for playlist details 
    add_multiple_form = AddMultipleForm()  # Add this for multiple track selection
    url_form = UrlForm()  # For URL submission
    
    # Set channel ID if available 
    selected_channel_id = None
    if user_voice_channel:
        selected_channel_id = user_voice_channel['id']
        search_form.channel_id.data = selected_channel_id
        music_control_form.channel_id.data = selected_channel_id
        shuffle_queue_form.channel_id.data = selected_channel_id
        playlist_form.channel_id.data = selected_channel_id
        add_multiple_form.channel_id.data = selected_channel_id
        url_form.channel_id.data = selected_channel_id
    
    # Default values
    search_results = []
    playlist_results = []
    playlist_videos = []
    playlist_details = None
    selected_playlist_id = None
    page_token = None
    next_page_token = None
    prev_page_token = None
    current_page = 1
    total_pages = 1
    total_results = 0
    has_next_page = False
    has_prev_page = False
    
    # Check if this is a playlist view request
    selected_playlist_id = request.args.get('playlist_id')
    if selected_playlist_id:
        # Get page token for pagination
        page_token = request.args.get('page_token')
        prev_page_token = request.args.get('prev_page_token')
        current_page = int(request.args.get('page', 1))
        
        # Fetch playlist details
        playlist_api_url = f"/api/youtube/playlist/{selected_playlist_id}"
        if page_token:
            playlist_api_url += f"?page_token={page_token}"
        
        playlist_response = await bot_api.get(playlist_api_url)
        if playlist_response.status_code == 200:
            playlist_data = await playlist_response.json()
            playlist_videos = playlist_data.get('items', [])
            playlist_details = playlist_data.get('playlist_details', {})
            next_page_token = playlist_data.get('next_page_token')
            total_results = playlist_data.get('total_results', 0)
            
            # Calculate pagination info
            has_next_page = next_page_token is not None
            has_prev_page = current_page > 1
            total_pages = (total_results + 49) // 50  # 50 items per page
            
            # Set playlist form data
            playlist_form.playlist_id.data = selected_playlist_id
            playlist_form.playlist_title.data = playlist_details.get('title', 'Unknown Playlist')
            add_multiple_form.playlist_id.data = selected_playlist_id
            add_multiple_form.page_token.data = page_token

    # Handle POST request (search)
    elif request.method == 'POST':
        form = await request.form
        query = form.get('query', '')
        search_type = form.get('search_type', 'comprehensive')
        channel_id = form.get('channel_id', '')
        
        # Check if query looks like a URL
        if 'youtube.com/' in query or 'youtu.be/' in query:
            # Process URL directly
            url_form.url.data = query
            url_form.channel_id.data = channel_id
            
            # Prefill form data for rendering
            search_form.query.data = query
            search_form.channel_id.data = channel_id
            
            # Fetch video details for the URL
            url_api_url = f"/api/youtube/video-info?url={query}"
            url_response = await bot_api.get(url_api_url)
            
            if url_response.status_code == 200:
                url_data = await url_response.json()
                video_info = url_data.get('video_info', {})
                
                # If it's a playlist URL, redirect to playlist view
                if url_data.get('type') == 'playlist':
                    playlist_id = url_data.get('playlist_id')
                    if playlist_id:
                        return redirect(url_for('youtube_search.youtube_search_route', 
                                              guild_id=guild_id, 
                                              playlist_id=playlist_id))
                
                # If it's a video URL, add it to search results
                elif video_info:
                    search_results = [{
                        'id': video_info.get('id'),
                        'title': video_info.get('title'),
                        'thumbnail': video_info.get('thumbnail'),
                        'channel': video_info.get('channel')
                    }]
        else:
            # Regular search
            search_api_url = f"/api/youtube/search?q={query}&type={search_type}"
            search_response = await bot_api.get(search_api_url)
            
            if search_response.status_code == 200:
                search_data = await search_response.json()
                
                # Handle different result types
                search_results = search_data.get('videos', [])
                playlist_results = search_data.get('playlists', [])
                
                # Prefill form data for rendering
                search_form.query.data = query
                search_form.search_type.data = search_type
                search_form.channel_id.data = channel_id
    
    # Get queue for selected channel
    queue_info = {"queue": [], "current_track": None}
    bot_state = {"connected": False, "playing": False, "paused": False}
    
    if selected_channel_id:
        # Get queue for the channel
        queue_api_url = f"/api/queue/{guild_id}/{selected_channel_id}"
        queue_response = await bot_api.get(queue_api_url)
        
        if queue_response.status_code == 200:
            queue_data = await queue_response.json()
            queue_info = queue_data
        
        # Get bot state for the channel
        state_api_url = f"/api/state/{guild_id}/{selected_channel_id}"
        state_response = await bot_api.get(state_api_url)
        
        if state_response.status_code == 200:
            bot_state = await state_response.json()
    
    return await render_template(
        'server_dashboard.html',
        guild_id=guild_id,
        guild_name=guild_name,
        guild_icon=guild_icon,
        voice_channels=voice_channels,
        user_voice_channel=user_voice_channel,
        selected_channel_id=selected_channel_id,
        search_results=search_results,
        playlist_results=playlist_results,
        playlist_videos=playlist_videos,
        playlist_details=playlist_details,
        selected_playlist_id=selected_playlist_id,
        page_token=page_token,
        next_page_token=next_page_token,
        prev_page_token=prev_page_token,
        current_page=current_page,
        total_pages=total_pages,
        total_results=total_results,
        has_next_page=has_next_page,
        has_prev_page=has_prev_page,
        queue=queue_info.get("queue", []),
        current_track=queue_info.get("current_track"),
        bot_state=bot_state,
        # Forms - make sure ALL forms are passed
        search_form=search_form,
        music_control_form=music_control_form,
        shuffle_queue_form=shuffle_queue_form,
        playlist_form=playlist_form,
        add_multiple_form=add_multiple_form,
        url_form=url_form
    )