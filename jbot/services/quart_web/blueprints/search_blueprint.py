"""
Search Blueprint for Quart Web Service
Handles YouTube search functionality
"""
from quart import Blueprint, render_template, request, redirect, url_for, current_app
from .helpers import login_required, get_voice_channels, get_user_voice_channel, get_queue_and_bot_state
from .forms_blueprint import (
    MusicControlForm, 
    ShuffleQueueForm, 
    SearchForm, 
    UrlForm, 
    ClearQueueForm,
    AddMultipleForm
)

# Create blueprint
search_blueprint = Blueprint('search', __name__)

@search_blueprint.route('/server/<guild_id>/search', methods=['GET'])
@login_required
async def youtube_search_route(guild_id):
    """Search YouTube for videos or display playlist details"""
    discord = current_app.discord
    discord_client = current_app.discord_client
    youtube_client = current_app.youtube_client
    
    # Get user's voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Get voice channels
    voice_channels = await get_voice_channels(guild_id)
    
    # Get guild info
    user_guilds = await discord.fetch_guilds()
    guild_info = next((g for g in user_guilds if str(g.id) == guild_id), None)
    
    # Safe attribute access
    guild_icon = getattr(guild_info, 'icon', None)
    guild_name = getattr(guild_info, 'name', f"Server {guild_id}")
    
    # Initialize forms with default values where needed
    selected_channel_id = None
    if user_voice_channel:
        selected_channel_id = user_voice_channel['id']
    
    # Create form instances with appropriate data
    search_form = SearchForm()
    music_control_form = MusicControlForm()
    shuffle_queue_form = ShuffleQueueForm()
    url_form = UrlForm()
    clear_queue_form = ClearQueueForm()
    add_multiple_form = AddMultipleForm()  # Add the new form
    
    # Set form values based on user's voice channel 
    if selected_channel_id:
        music_control_form.channel_id.data = selected_channel_id
        shuffle_queue_form.channel_id.data = selected_channel_id
        search_form.channel_id.data = selected_channel_id
        url_form.channel_id.data = selected_channel_id
        add_multiple_form.channel_id.data = selected_channel_id  # Set channel_id for the multiple form
    
    clear_queue_form.guild_id.data = guild_id
    
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
        # Set playlist_id for the add_multiple_form
        add_multiple_form.playlist_id.data = selected_playlist_id
        
        # Get page token for pagination
        page_token = request.args.get('page_token')
        prev_page_token = request.args.get('prev_page_token')
        current_page = int(request.args.get('page', 1))
        
        # Fetch playlist details
        playlist_details = await youtube_client.get_playlist_details(selected_playlist_id)
        
        # Get playlist videos
        playlist_videos, next_page_token, total_results = await youtube_client.get_playlist_videos(
            selected_playlist_id, page_token
        )
        
        # Calculate pagination info
        has_next_page = next_page_token is not None
        has_prev_page = current_page > 1
        total_pages = (total_results + 49) // 50  # 50 items per page

    # Handle search query from GET parameters
    elif request.args.get('query'):
        # Process the search form
        query = request.args.get('query', '')
        search_type = request.args.get('search_type', 'comprehensive')
        channel_id = request.args.get('channel_id', '')
        
        # Set search form values for the template
        search_form.query.data = query
        search_form.search_type.data = search_type
        search_form.channel_id.data = channel_id
        
        # Check if query looks like a URL
        if 'youtube.com/' in query or 'youtu.be/' in query:
            # Process URL directly
            url_form.url.data = query
            url_form.channel_id.data = channel_id
            
            # Check if it's a playlist URL
            playlist_id = youtube_client.extract_playlist_id(query)
            if playlist_id:
                return redirect(url_for('search.youtube_search_route', 
                                      guild_id=guild_id, 
                                      playlist_id=playlist_id))
            
            # If it's a video URL, extract ID and add to search results
            video_id = youtube_client.extract_video_id(query)
            if video_id:
                video_details = await youtube_client.get_video_details(video_id)
                search_results = [{
                    'id': video_id,
                    'title': video_details.get('title', 'Unknown Video'),
                    'thumbnail': video_details.get('thumbnail', ''),
                    'channel': video_details.get('channel', 'Unknown Channel'),
                    'duration': video_details.get('duration', 0)
                }]
        else:
            # Regular search
            if search_type in ['video', 'comprehensive']:
                search_results = await youtube_client.search_videos(query)
            
            if search_type in ['playlist', 'comprehensive']:
                playlist_results = await youtube_client.search_playlists(query)
    
    # Get queue for selected channel
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, selected_channel_id)
    
    # Render the template with all necessary data
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
        # Forms
        search_form=search_form,
        music_control_form=music_control_form,
        shuffle_queue_form=shuffle_queue_form,
        url_form=url_form,
        clear_queue_form=clear_queue_form,
        add_multiple_form=add_multiple_form
    )