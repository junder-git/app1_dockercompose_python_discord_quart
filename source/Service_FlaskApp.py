from functools import wraps
from quart import Quart, render_template, redirect, url_for, session, request, flash
import aiohttp
from quart_discord import DiscordOAuth2Session
import os
from dotenv import load_dotenv
from Class_DiscordBotAPI import DiscordBotAPI
from Class_YouTube import YouTubeService
from Class_MusicPlayer import MusicService

# Load environment variables from .env file
load_dotenv()
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # Required for OAuth 2 over http
DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
IPC_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')

# Initialize the services
youtube_service = YouTubeService(api_key=YOUTUBE_API_KEY)
music_service = MusicService(api_key=YOUTUBE_API_KEY)

app = Quart(__name__)
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config["DISCORD_CLIENT_ID"] = os.environ.get('DISCORD_CLIENT_ID')
app.config["DISCORD_CLIENT_SECRET"] = os.environ.get('DISCORD_CLIENT_SECRET')
app.config["DISCORD_REDIRECT_URI"] = os.environ.get('DISCORD_REDIRECT_URI')

discord = DiscordOAuth2Session(app)

# Initialize the Bot API client
bot_api = DiscordBotAPI(
    host="discord-bot",  # Docker service name
    port=5001,           # Port exposed in docker-compose
    secret_key=IPC_SECRET_KEY
)

# Add cleanup on app exit
@app.teardown_appcontext
async def shutdown_session(exception=None):
    await bot_api.close()

# Login required decorator
def login_required(f):
    @wraps(f)
    async def decorated_function(*args, **kwargs):
        print(f"Login check - Session contains: {list(session.keys())}")
        if 'user_id' not in session:
            print("No user_id in session, redirecting to login")
            return redirect(url_for('login'))
        print(f"User {session.get('username')} authenticated, proceeding to route")
        return await f(*args, **kwargs)
    return decorated_function

@app.route("/")
async def index():
    return await render_template("index.html", authorized=await discord.authorized)

@app.route("/login")
async def login():
    # Clear any existing session data to ensure a fresh login
    session.clear()
    
    # Make sure we're requesting all the scopes we need
    scope = ["identify", "guilds"]
    authorization_url = await discord.create_session(scope=scope)
    
    return authorization_url

@app.route("/callback")
async def callback():
    try:
        # Complete the OAuth flow
        data = await discord.callback()
        
        # Get the user
        user = await discord.fetch_user()
        
        # Store user information in session
        session['user_id'] = user.id
        session['username'] = user.name
        
        # Also store the access token for further API calls
        if hasattr(discord, 'token'):
            session['discord_token'] = discord.token
        
        # Print debug information
        print(f"OAuth callback successful for user: {user.name} ({user.id})")
        print(f"Session after callback: {list(session.keys())}")
        
        # Fetch user guilds to verify API access is working
        try:
            guilds = await discord.fetch_guilds()
            print(f"Successfully fetched {len(guilds)} guilds for user")
        except Exception as e:
            print(f"Error fetching guilds: {e}")
        
        return redirect(url_for("dashboard"))
    except Exception as e:
        print(f"Error in OAuth callback: {e}")
        # Clear the session on error to prevent loops
        session.clear()
        return redirect(url_for("index"))

@app.route("/logout")
async def logout():
    # Revoke the token with Discord if possible
    if discord.authorized:
        try:
            await discord.revoke()
        except:
            pass
    
    # Clear the session
    session.clear()
    
    # Redirect to the home page
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
async def dashboard():
    try:
        # First, verify we have the necessary session data
        if 'user_id' not in session:
            print("No user_id in session, redirecting to login")
            return redirect(url_for("login"))
            
        # Get guild information
        guild_count = 0
        guild_ids = []
        try:
            guild_count = await bot_api.get_guild_count()
            guild_ids = await bot_api.get_guild_ids()
            print(f"Bot guild count: {guild_count}")
            print(f"Bot guild IDs: {guild_ids}")
        except Exception as e:
            print(f"Error getting bot guild info: {e}")
            # Continue anyway, showing guilds without bot presence
        
        # Fetch user
        user = await discord.fetch_user()
        
        # Fetch user guilds
        user_guilds = await discord.fetch_guilds()
        print(f"User has {len(user_guilds)} guilds")
        
        # Print user guild IDs for debugging
        user_guild_ids = [str(g.id) for g in user_guilds]  # Convert to strings
        print(f"User guild IDs: {user_guild_ids}")
        
        # Type-safe comparison of guild IDs
        same_guilds = []
        for guild in user_guilds:
            guild_id_str = str(guild.id)
            print(f"Checking guild: {guild.name} (ID: {guild_id_str})")
            
            if guild_id_str in guild_ids:
                print(f"Match found! Guild: {guild.name}")
                same_guilds.append(guild)
        
        print(f"Found {len(same_guilds)} mutual guilds out of {len(user_guilds)} total user guilds")
        print(f"Same guilds: {[g.name for g in same_guilds]}")
        
        has_no_mutual_guilds = len(same_guilds) == 0
        print(f"has_no_mutual_guilds = {has_no_mutual_guilds}")
                
        # Pass config for bot invite link
        config = {
            "DISCORD_CLIENT_ID": app.config["DISCORD_CLIENT_ID"]
        }
        
        return await render_template(
            "dashboard.html", 
            guild_count=guild_count, 
            matching=same_guilds, 
            user=user, 
            guilds=same_guilds,  # Using same_guilds for both matching and guilds
            has_no_mutual_guilds=has_no_mutual_guilds,
            bot_check_errors=False,
            config=config
        )
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Log the full traceback for better debugging
        import traceback
        traceback.print_exc()
        # Clear session and redirect to login on error
        session.clear()
        return redirect(url_for("login"))

# Main dashboard route - focuses only on displaying the dashboard
@app.route('/server/<guild_id>/dashboard')
@login_required
async def server_dashboard(guild_id):
    """Server dashboard for viewing voice channels and music status"""
    # Get guild info
    user_guilds = await discord.fetch_guilds()
    guild_info = next((g for g in user_guilds if str(g.id) == guild_id), None)
    
    if not guild_info:
        return redirect(url_for('dashboard'))
    
    # Get voice channels
    voice_channels = await get_voice_channels(guild_id)
    
    # Get user's voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Get current selected channel (if any)
    selected_channel_id = request.args.get('channel_id', '')
    
    # If no channel is selected but user is in a voice channel, use that
    if not selected_channel_id and user_voice_channel:
        selected_channel_id = user_voice_channel['id']
    
    # Get queue for selected channel (if applicable)
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, selected_channel_id, voice_channels)
    
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
        bot_state=bot_state
    )

@app.route('/server/<guild_id>/music/control')
@login_required
async def music_control(guild_id):
    """Handle music control commands: join, skip, pause, resume, stop"""
    command = request.args.get('command')
    channel_id = request.args.get('channel_id')    
    if not command or not channel_id:
        flash("Missing command or channel ID", "error")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
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
            # Call the new disconnect function with preserve_queue=False to clear the queue
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
    return redirect(url_for('server_dashboard', guild_id=guild_id, channel_id=channel_id))

@app.route('/server/<guild_id>/queue/clear')
@login_required
async def clear_queue(guild_id):
    """Explicitly clear the queue for a guild"""
    try:
        result = await bot_api.clear_queue(guild_id)
        if result.get('success'):
            flash("Music queue cleared", "success")
        else:
            flash(f"Error clearing queue: {result.get('error')}", "error")
    except Exception as e:
        flash(f"Error clearing queue: {str(e)}", "error")
    
    return redirect(url_for('server_dashboard', guild_id=guild_id))

@app.route('/server/<guild_id>/queue/add')
@login_required
async def add_to_queue(guild_id):
    """Handle adding videos to the queue"""
    # Get the requested channel_id from the URL parameters
    channel_id = request.args.get('channel_id')
    video_id = request.args.get('video_id')
    video_title = request.args.get('video_title', 'Unknown Video')
    
    if not channel_id or not video_id:
        flash("Missing channel ID or video ID", "error")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    # Get user's current voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Add debug logging to help identify the issue
    print(f"Add to queue: User voice channel: {user_voice_channel}")
    print(f"Add to queue: Requested channel: {channel_id}")
    
    # More tolerant check - if we got a user_voice_channel object, use its ID
    user_voice_channel_id = user_voice_channel['id'] if user_voice_channel else None
    
    # Debug log the values we're comparing
    print(f"Comparing user channel ID: {user_voice_channel_id} with requested channel ID: {channel_id}")
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel_id:
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    # Try to add the track
    try:
        result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
        if result.get('success'):
            flash(f"Added '{video_title}' to queue", "success")
        else:
            flash(f"Error adding to queue: {result.get('error')}", "error")
    except Exception as e:
        flash(f"Error adding to queue: {str(e)}", "error")
    
    # Redirect back to search results or dashboard with the selected channel
    return_to = request.args.get('return_to', 'dashboard')
    if return_to == 'search':
        playlist_id = request.args.get('playlist_id')
        page_token = request.args.get('page_token')
        if playlist_id:
            return redirect(url_for('youtube_search', guild_id=guild_id, playlist_id=playlist_id, page_token=page_token))
        else:
            return redirect(url_for('youtube_search', guild_id=guild_id))
    else:
        return redirect(url_for('server_dashboard', guild_id=guild_id))

# Update the youtube_search route to use the shared services
@app.route('/server/<guild_id>/search', methods=['GET', 'POST'])
@login_required
async def youtube_search(guild_id):
    """Handle YouTube search requests for videos and playlists with pagination"""
    search_results = []
    playlist_results = []
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
        return redirect(url_for('dashboard'))
    
    # Get all voice channels
    all_voice_channels = await get_voice_channels(guild_id)
    
    # Get user's voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
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
    if request.method == 'POST' and user_voice_channel:
        form = await request.form
        search_type = form.get('search_type', 'video')
        
        if 'query' in form:
            query = form.get('query')
            if query:
                if search_type == 'video':
                    # Use the YouTube service for video search
                    search_results = await youtube_service.search_videos(query)
                elif search_type == 'playlist':
                    # Use the YouTube service for playlist search
                    playlist_results = await youtube_service.search_playlists(query)
    elif request.method == 'POST' and not user_voice_channel:
        flash("You must join a voice channel in Discord before searching for music", "warning")
    
    # Always use the user's current voice channel as the selected channel
    selected_channel_id = user_voice_channel['id'] if user_voice_channel else None
    
    # Get queue for the selected channel (if user is in a voice channel)
    queue_info = {"queue": [], "current_track": None}
    bot_state = {
        'connected': False,
        'is_playing': False,
        'voice_channel_id': None,
        'voice_channel_name': None
    }
    
    if selected_channel_id:
        queue_info, bot_state = await get_queue_and_bot_state(guild_id, selected_channel_id, all_voice_channels)
    
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
        playlist_videos=playlist_videos,
        playlist_details=playlist_details,
        selected_playlist_id=selected_playlist_id,
        selected_channel_id=selected_channel_id,
        user_voice_channel=user_voice_channel,
        queue=queue_info.get("queue", []),
        current_track=queue_info.get("current_track"),
        bot_state=bot_state,
        search_type=search_type,
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

@app.route('/server/<guild_id>/queue/add_multiple', methods=['POST'])
@login_required
async def add_multiple_to_queue(guild_id):
    """Handle adding multiple videos to the queue from a playlist"""
    # Debug the form data first
    form = await request.form
    print(f"Form data: {dict(form)}")
    
    channel_id = form.get('channel_id')
    if not channel_id:
        flash("Missing channel ID", "error")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    # Get user's current voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel:
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    # Get all selected video IDs and titles
    video_ids = form.getlist('video_ids')
    video_titles = form.getlist('video_titles')
    
    print(f"Video IDs: {video_ids}")
    print(f"Video Titles: {video_titles}")
    
    # Make sure we have data to process
    if not video_ids or len(video_ids) == 0:
        flash("No videos selected", "warning")
        return redirect(url_for('youtube_search', guild_id=guild_id))
    
    # Process each selected video individually to ensure they're added
    added_count = 0
    for i, video_id in enumerate(video_ids):
        # Get the corresponding title if available
        video_title = "Unknown Video"
        if i < len(video_titles):
            video_title = video_titles[i]
        
        try:
            result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
            if result.get('success'):
                added_count += 1
            else:
                flash(f"Error adding '{video_title}' to queue: {result.get('error')}", "error")
        except Exception as e:
            flash(f"Error adding video to queue: {str(e)}", "error")
    
    if added_count > 0:
        flash(f"Added {added_count} videos to queue", "success")
    
    # Go back to the search page or the playlist page if a playlist_id was provided
    playlist_id = form.get('playlist_id')
    page_token = form.get('page_token')
    if playlist_id:
        return redirect(url_for('youtube_search', guild_id=guild_id, playlist_id=playlist_id, page_token=page_token))
    else:
        return redirect(url_for('youtube_search', guild_id=guild_id))

@app.route('/server/<guild_id>/queue/add_entire_playlist', methods=['POST'])
@login_required
async def add_entire_playlist(guild_id):
    """Handle adding an entire YouTube playlist to the queue"""
    form = await request.form
    playlist_id = form.get('playlist_id')
    channel_id = form.get('channel_id')
    playlist_title = form.get('playlist_title', 'Unknown Playlist')
    
    if not playlist_id or not channel_id:
        flash("Missing playlist ID or channel ID", "error")
        return redirect(url_for('youtube_search', guild_id=guild_id))
    
    # Get user's current voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel:
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('youtube_search', guild_id=guild_id))
    
    # Start by getting the first batch of videos
    added_count = 0
    page_token = None
    total_added = 0
    max_pages = 10  # Limit to 10 pages (500 videos) to prevent abuse
    
    # Process videos in batches
    for _ in range(max_pages):
        videos, next_page_token, _ = await youtube_service.get_playlist_videos(playlist_id, page_token)
        
        if not videos:
            break
            
        # Add each video to the queue
        for video in videos:
            try:
                result = await bot_api.add_to_queue(guild_id, channel_id, video['id'], video['title'])
                if result.get('success'):
                    total_added += 1
            except Exception as e:
                print(f"Error adding video to queue: {e}")
                # Continue with next video
                continue
                
        # If there's no next page, we're done
        if not next_page_token:
            break
            
        # Update page token for next batch
        page_token = next_page_token
    
    if total_added > 0:
        flash(f"Added {total_added} videos from playlist '{playlist_title}' to queue", "success")
    else:
        flash("Failed to add videos from playlist to queue", "error")
    
    # Redirect to dashboard to show the queue
    return redirect(url_for('server_dashboard', guild_id=guild_id))

@app.route('/server/<guild_id>/add_by_url', methods=['POST'])
@login_required
async def add_by_url(guild_id):
    """Handle adding videos by URL - supports both single videos and playlists"""
    form = await request.form
    url = form.get('url')
    channel_id = form.get('channel_id')
    
    if not url or not channel_id:
        flash("Missing URL or channel ID", "error")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    # Get user's current voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
    # Verify the user is actually in a voice channel
    if not user_voice_channel:
        flash("You must join a voice channel before adding music to the queue", "warning")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    # Use the shared service for URL handling
    is_playlist = youtube_service.extract_playlist_id(url) is not None
    
    try:
        if is_playlist:
            # Extract playlist ID
            playlist_id = youtube_service.extract_playlist_id(url)
            if not playlist_id:
                flash("Invalid YouTube playlist URL", "error")
                return redirect(url_for('server_dashboard', guild_id=guild_id))
            
            # Redirect to playlist confirmation page
            return redirect(url_for('playlist_confirmation', 
                                   guild_id=guild_id, 
                                   playlist_id=playlist_id, 
                                   channel_id=channel_id))
        else:
            # Extract video ID
            video_id = youtube_service.extract_video_id(url)
            if not video_id:
                flash("Invalid YouTube video URL", "error")
                return redirect(url_for('server_dashboard', guild_id=guild_id))
            
            # Get video details using the YouTube service
            video_details = await youtube_service.get_video_details(video_id)
            video_title = video_details.get('title', 'Unknown Video')
            
            # Add to queue
            result = await bot_api.add_to_queue(guild_id, channel_id, video_id, video_title)
            if result.get('success'):
                flash(f"Added '{video_title}' to queue", "success")
            else:
                flash(f"Error adding video to queue: {result.get('error')}", "error")
        
    except Exception as e:
        flash(f"Error processing URL: {str(e)}", "error")
    
    # Redirect back to dashboard
    return redirect(url_for('server_dashboard', guild_id=guild_id))

# Helper functions that were not moved to the services
async def get_user_voice_channel(guild_id, user_id):
    """
    Get the voice channel a user is currently in
    
    Args:
        guild_id (str): Discord guild ID
        user_id (str): Discord user ID
    
    Returns:
        dict: Voice channel information including id and name, or None if not in a channel
    """
    headers = {'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
    channel_id = None
    
    # Try getting from bot API first
    try:
        voice_state = await bot_api.get_user_voice_state(guild_id, user_id)
        print(f"Voice state from bot API: {voice_state}")
        if voice_state and 'channel_id' in voice_state:
            channel_id = voice_state['channel_id']
            print(f"Found voice channel ID from bot API: {channel_id}")
    except Exception as e:
        print(f"Error getting voice state from bot API: {e}")
    
    # If we couldn't get from bot API, try Discord API
    if not channel_id:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        member_data = await response.json()
                        # Try to find voice state information
                        print(f"Member data for {user_id}: {member_data}")
                        if 'voice' in member_data and member_data['voice'] and 'channel_id' in member_data['voice']:
                            channel_id = member_data['voice']['channel_id']
                            print(f"Found voice channel ID in member data: {channel_id}")
        except Exception as e:
            print(f"Error getting voice state from bot API: {e}")
    
        # If we couldn't get from bot API, try Discord API
        if not channel_id:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"https://discord.com/api/v10/guilds/{guild_id}/members/{user_id}",
                        headers=headers
                    ) as response: 
                        if response.status == 200:
                            voice_states = await response.json()
                            print(f"Voice states for guild {guild_id}: {voice_states}")
                            for state in voice_states:
                                if state.get('user_id') == user_id and state.get('channel_id'):
                                    channel_id = state.get('channel_id')
                                    print(f"Found voice channel ID in voice states: {channel_id}")
                                    break
            except Exception as e:
                print(f"Error getting voice states: {e}")
    
    # If we have a channel ID, get the channel details
    if channel_id:
        # Get all voice channels and find the one with matching ID
        try:
            voice_channels = await get_voice_channels(guild_id)
            for channel in voice_channels:
                if channel['id'] == channel_id:
                    print(f"Found matching voice channel details: {channel}")
                    return channel  # Return the full channel object with id, name, etc.
            
            # If we couldn't find the channel in the list (might happen if API is slow to update)
            print(f"Channel ID {channel_id} found but no matching channel in voice_channels list")
            return {'id': channel_id, 'name': 'Voice Channel'}
        except Exception as e:
            print(f"Error getting voice channel details: {e}")
            # If we can't get details, at least return the ID
            return {'id': channel_id, 'name': 'Voice Channel'}
    
    print(f"No voice channel found for user {user_id} in guild {guild_id}")
    return None

async def get_voice_channels(guild_id):
    """Get voice channels for a guild"""
    headers = {'Authorization': f"Bot {DISCORD_BOT_TOKEN}"}
    channels = []
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"https://discord.com/api/guilds/{guild_id}/channels", 
            headers=headers
        ) as response:
            if response.status == 200:
                channels = await response.json()
    # Filter voice channels
    return [c for c in channels if c['type'] == 2]  # type 2 is voice channel

async def get_queue_and_bot_state(guild_id, selected_channel_id, voice_channels):
    """Get queue information and bot state for a specific channel"""
    queue_info = {"queue": [], "current_track": None}
    bot_state = {
        'connected': False,
        'is_playing': False,
        'voice_channel_id': None,
        'voice_channel_name': None
    }
    
    if selected_channel_id:
        try:
            queue_info = await bot_api.get_queue(guild_id, selected_channel_id)
            
            # Update bot state based on queue info
            if queue_info.get('is_connected'):
                bot_state['connected'] = True
                bot_state['is_playing'] = queue_info.get('is_playing', False)
                
                # Find the voice channel name
                for channel in voice_channels:
                    if channel['id'] == selected_channel_id:
                        bot_state['voice_channel_id'] = channel['id']
                        bot_state['voice_channel_name'] = channel['name']
                        break
        except Exception as e:
            print(f"Error getting queue: {e}")
    
    return queue_info, bot_state

@app.route('/server/<guild_id>/playlist_confirmation')
@login_required
async def playlist_confirmation(guild_id):
    """Confirmation page for adding YouTube playlists"""
    playlist_id = request.args.get('playlist_id')
    channel_id = request.args.get('channel_id')
    
    if not playlist_id or not channel_id:
        flash("Missing playlist ID or channel ID", "error")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    # Get guild info
    user_guilds = await discord.fetch_guilds()
    guild_info = next((g for g in user_guilds if str(g.id) == guild_id), None)
    if not guild_info:
        return redirect(url_for('dashboard'))
    
    # Get voice channels
    voice_channels = await get_voice_channels(guild_id)
    
    # Get user's voice channel
    user = await discord.fetch_user()
    user_id = str(user.id)
    user_voice_channel = await get_user_voice_channel(guild_id, user_id)
    
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

@app.route('/server/<guild_id>/queue/reorder', methods=['POST'])
@login_required
async def reorder_queue(guild_id):
    """Handle reordering of tracks in the queue"""
    form = await request.form
    channel_id = form.get('channel_id')
    old_index = form.get('old_index')
    new_index = form.get('new_index')
    
    if not all([channel_id, old_index, new_index]):
        flash("Missing parameters for queue reordering", "error")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    try:
        # Convert to integers
        old_index = int(old_index)
        new_index = int(new_index)
        
        # Call the API to reorder the queue
        result = await bot_api.reorder_queue(guild_id, channel_id, old_index, new_index)
        
        if result.get('success'):
            flash("Queue order updated", "success")
        else:
            flash(f"Error reordering queue: {result.get('error')}", "error")
    except Exception as e:
        flash(f"Error reordering queue: {str(e)}", "error")
        
    # Redirect back to the dashboard
    return redirect(url_for('server_dashboard', guild_id=guild_id, channel_id=channel_id))

@app.route('/server/<guild_id>/music/shuffle')
@login_required
async def shuffle_queue(guild_id):
    """Shuffle the current music queue"""
    channel_id = request.args.get('channel_id')
    if not channel_id:
        flash("Missing channel ID", "error")
        return redirect(url_for('server_dashboard', guild_id=guild_id))
    
    try:
        # Call the bot API to shuffle the queue
        result = await bot_api.shuffle_queue(guild_id, channel_id)
        if result.get('success'):
            flash("Music queue shuffled", "success")
        else:
            flash(f"Error shuffling queue: {result.get('error')}", "error")
    except Exception as e:
        flash(f"Error shuffling queue: {str(e)}", "error")
    
    # Redirect back to dashboard with the selected channel
    return redirect(url_for('server_dashboard', guild_id=guild_id, channel_id=channel_id))

@app.route('/server/<guild_id>/queue/ajax')
@login_required
async def queue_ajax(guild_id):
    # Get the channel ID from query parameters
    channel_id = request.args.get('channel_id')
    
    # Get voice channels to get the channel name
    voice_channels = await get_voice_channels(guild_id)
    
    # Get queue info and bot state
    queue_info, bot_state = await get_queue_and_bot_state(guild_id, channel_id, voice_channels)
    
    # Return the queue information in JSON format
    return {
        "queue": queue_info.get("queue", []),
        "current_track": queue_info.get("current_track"),
        "is_connected": bot_state.get("connected", False),
        "is_playing": bot_state.get("is_playing", False),
        "is_paused": queue_info.get("is_paused", False)
    }

@app.before_serving
async def before_serving():
    """Initialize resources before the server starts"""
    # Nothing to initialize yet

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")