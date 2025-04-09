import os
import discord
import asyncio
from discord.ext import commands
from aiohttp import web
from dotenv import load_dotenv
from collections import defaultdict
import random
from Class_MusicPlayer import MusicService
from Class_YouTube import YouTubeService
from Class_DiscordView import MusicControlView

# Load environment variables from .env file
load_dotenv()

DISCORD_BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN')
IPC_SECRET_KEY = os.environ.get('FLASK_SECRET_KEY')
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')

# Initialize shared services
youtube_service = YouTubeService(api_key=YOUTUBE_API_KEY)
music_service = MusicService(api_key=YOUTUBE_API_KEY)

# Set up intents
intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_server = None
        # Music queue handling - rename attribute to avoid conflicts
        self.music_queues = defaultdict(list)  # Queue ID -> list of tracks
        self.currently_playing = {}  # Queue ID -> current track info
        self.voice_connections = {}  # Queue ID -> voice client
        # Track control panels sent to text channels
        self.control_panels = {}  # Channel ID -> Message ID
        self.playlist_processing = {}  # Queue ID -> boolean flag to interrupt playlist processing
        
    async def setup_hook(self):
        """This is called when the bot starts up"""
        # Start the API server
        await self.start_api_server()
        print("API server started")

    async def on_ready(self):
        """Called upon the READY event"""
        print("Bot is ready.")
        print(f"Logged in as {self.user.name} ({self.user.id})")
        
        # Print all guilds the bot is in
        print("Bot is in the following guilds:")
        for guild in self.guilds:
            print(f"- {guild.name} (ID: {guild.id})")

    async def follow_to_voice_channel(self, guild_id, current_channel_id, new_channel_id, user):
        """Follow a user to a new voice channel, preserving the queue and current track"""
        try:
            # Get the current queue ID
            old_queue_id = self.get_queue_id(guild_id, current_channel_id)
            
            # Get the new queue ID
            new_queue_id = self.get_queue_id(guild_id, new_channel_id)
            
            # Get the guild
            guild = self.get_guild(int(guild_id))
            if not guild:
                return {"success": False, "message": "Guild not found"}
            
            # Get the new voice channel
            new_voice_channel = guild.get_channel(int(new_channel_id))
            if not new_voice_channel or not isinstance(new_voice_channel, discord.VoiceChannel):
                return {"success": False, "message": "Voice channel not found"}
            
            # Save current playback state and queue
            current_track = self.currently_playing.get(old_queue_id)
            was_playing = False
            was_paused = False
            
            # Check if we were connected and playing/paused
            if old_queue_id in self.voice_connections and self.voice_connections[old_queue_id].is_connected():
                voice_client = self.voice_connections[old_queue_id]
                was_playing = voice_client.is_playing()
                was_paused = voice_client.is_paused()
                
                # Stop current playback if any
                if was_playing or was_paused:
                    voice_client.stop()
                
                # Disconnect from the current voice channel
                await voice_client.disconnect(force=True)
                self.voice_connections.pop(old_queue_id, None)
            
            # Connect to the new voice channel
            try:
                new_voice_client = await new_voice_channel.connect()
                self.voice_connections[new_queue_id] = new_voice_client
            except Exception as e:
                print(f"Error connecting to new voice channel: {e}")
                return {"success": False, "message": f"Failed to connect to new voice channel: {str(e)}"}
            
            # Transfer queue from old to new channel
            self.music_queues[new_queue_id] = self.music_queues.pop(old_queue_id, [])
            
            # Set the interruption flag to stop any ongoing playlist processing
            self.playlist_processing[old_queue_id] = True
            
            # Update queue IDs in any ongoing operations
            self.playlist_processing[new_queue_id] = self.playlist_processing.pop(old_queue_id, False)
            
            # If we had a current track, add it back to the front of the queue to resume
            if current_track and (was_playing or was_paused):
                self.music_queues[new_queue_id].insert(0, current_track)
                # Clear the currently playing track for the old queue
                self.currently_playing.pop(old_queue_id, None)
                
                # Immediately start playback if we were playing
                if was_playing:
                    asyncio.create_task(self.play_next(guild_id, new_channel_id))
            
            # Update all control panels
            for text_channel_id, message_id in list(self.control_panels.items()):
                try:
                    text_channel = guild.get_channel(text_channel_id)
                    if text_channel:
                        await self.send_control_panel(text_channel, new_voice_channel, guild_id)
                except Exception as e:
                    print(f"Error updating control panel: {e}")
            
            return {
                "success": True,
                "message": f"Followed {user.display_name} to {new_voice_channel.name}"
            }
            
        except Exception as e:
            print(f"Error following to voice channel: {e}")
            return {"success": False, "message": f"Error: {str(e)}"}

    async def on_message(self, message):
        """Handle incoming messages"""
        # Don't respond to own messages
        if message.author == self.user:
            return
        
        # Process commands first
        await self.process_commands(message)
        
        # Check for the "jbot" trigger word
        if message.content.lower() == "jbot":
            # Check if the user is in a voice channel
            if message.author.voice and message.author.voice.channel:
                voice_channel = message.author.voice.channel
                
                # Create a response with UI controls
                await self.join_and_show_controls(message.channel, voice_channel, message.guild.id)
            else:
                await message.channel.send("You need to be in a voice channel first!", delete_after=10)
    
    # SHARED UTILITY METHODS
    
    def get_queue_id(self, guild_id, channel_id):
        """Create a unique queue ID from guild and channel IDs"""
        return f"{guild_id}_{channel_id}"
    
    async def check_same_voice_channel(self, user, channel_id):
        """Check if a user is in the specified voice channel"""
        return user.voice and str(user.voice.channel.id) == channel_id
    
    async def get_voice_client(self, guild_id, channel_id, connect=False):
        """Get or create a voice client for the specified channel"""
        queue_id = self.get_queue_id(guild_id, channel_id)
        
        # Return existing connection if available
        if queue_id in self.voice_connections and self.voice_connections[queue_id].is_connected():
            return self.voice_connections[queue_id], queue_id
        
        # Connect if requested and not already connected
        if connect:
            guild = self.get_guild(int(guild_id))
            if not guild:
                return None, queue_id
                
            voice_channel = guild.get_channel(int(channel_id))
            if not voice_channel:
                return None, queue_id
                
            try:
                voice_client = await voice_channel.connect()
                self.voice_connections[queue_id] = voice_client
                return voice_client, queue_id
            except Exception as e:
                print(f"Error connecting to voice channel: {e}")
                return None, queue_id
        
        return None, queue_id
    
    # PLAYER CONTROL METHODS
    async def toggle_playback(self, guild_id, channel_id):
        """Toggle play/pause state for a voice client"""
        voice_client, queue_id = await self.get_voice_client(guild_id, channel_id)
        
        if not voice_client:
            return {"success": False, "message": "Not connected to a voice channel"}
        
        if voice_client.is_paused():
            voice_client.resume()
            return {"success": True, "message": "▶️ Resumed playback"}
        elif voice_client.is_playing():
            voice_client.pause()
            return {"success": True, "message": "⏸️ Paused playback"}
        else:
            # Not playing or paused, try to start playing if there's a queue
            if self.music_queues[queue_id]:
                asyncio.create_task(self.play_next(guild_id, channel_id))
                return {"success": True, "message": "▶️ Started playback"}
            else:
                return {"success": False, "message": "No tracks in queue to play"}
    
    async def skip_track(self, guild_id, channel_id):
        """Skip the current track"""
        voice_client, queue_id = await self.get_voice_client(guild_id, channel_id)
        
        if not voice_client:
            return {"success": False, "message": "Not connected to a voice channel"}
        
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
            return {"success": True, "message": "⏭️ Skipped to next track"}
        else:
            return {"success": False, "message": "Nothing is playing to skip"}
    
    async def stop_playback(self, guild_id, channel_id):
        """Stop playback and clear the queue"""
        voice_client, queue_id = await self.get_voice_client(guild_id, channel_id)
        
        if not voice_client:
            return {"success": False, "message": "Not connected to a voice channel"}
        
        # Set flag to interrupt any ongoing playlist additions
        self.playlist_processing[queue_id] = True
        
        # Clear queue and stop playing
        self.music_queues[queue_id] = []
        self.currently_playing.pop(queue_id, None)
        
        if voice_client.is_playing() or voice_client.is_paused():
            voice_client.stop()
        
        return {"success": True, "message": "⏹️ Stopped playback and cleared queue"}
    
    async def shuffle_queue(self, guild_id, channel_id):
        """Shuffle the queue"""
        queue_id = self.get_queue_id(guild_id, channel_id)
        
        if not self.music_queues[queue_id]:
            return {"success": False, "message": "Queue is empty, nothing to shuffle"}
        
        random.shuffle(self.music_queues[queue_id])
        return {"success": True, "message": "🔀 Queue shuffled"}
    
    async def add_to_queue(self, guild_id, channel_id, video_id, video_title):
        """Add a track to the queue and start playing if needed"""
        voice_client, queue_id = await self.get_voice_client(guild_id, channel_id, connect=True)
        
        if not voice_client:
            return {"success": False, "message": "Could not connect to voice channel"}
        
        # Add to queue
        self.music_queues[queue_id].append({
            "id": video_id,
            "title": video_title,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })
        
        # If we're not playing anything in this queue, start playing
        if queue_id not in self.currently_playing:
            asyncio.create_task(self.play_next(guild_id, channel_id))
        
        # Update control panels
        await self.update_control_panel(guild_id, channel_id)
        
        return {
            "success": True, 
            "message": f"Added to queue: {video_title}",
            "queue_length": len(self.music_queues[queue_id])
        }
    
    async def reorder_queue(self, guild_id, channel_id, old_index, new_index):
        """Move a track in the queue from old_index to new_index"""
        queue_id = self.get_queue_id(guild_id, channel_id)
        
        # Make sure indices are valid
        if not self.music_queues[queue_id] or old_index < 0 or old_index >= len(self.music_queues[queue_id]) or \
        new_index < 0 or new_index >= len(self.music_queues[queue_id]):
            return {"success": False, "message": "Invalid index"}
        
        # Move the track from old_index to new_index
        track = self.music_queues[queue_id].pop(old_index)
        self.music_queues[queue_id].insert(new_index, track)
        
        # Update control panels
        await self.update_control_panel(guild_id, channel_id)
        
        return {
            "success": True,
            "message": f"Track moved from position {old_index} to {new_index}"
        }
    
    async def clear_queue(self, guild_id, channel_id=None):
        """Clear queue(s) for a guild, optionally for a specific channel"""
        queues_cleared = 0
        channel_ids = []
        
        if channel_id:
            # Clear a specific queue
            queue_id = self.get_queue_id(guild_id, channel_id)
            self.music_queues[queue_id] = []
            self.currently_playing.pop(queue_id, None)
            channel_ids.append(channel_id)
            queues_cleared = 1
        else:
            # Clear all queues for this guild
            for queue_id in list(self.music_queues.keys()):
                if queue_id.startswith(f"{guild_id}_"):
                    self.music_queues[queue_id] = []
                    self.currently_playing.pop(queue_id, None)
                    this_channel_id = queue_id.split('_')[1]
                    channel_ids.append(this_channel_id)
                    queues_cleared += 1
        
        # Update control panels
        for ch_id in channel_ids:
            await self.update_control_panel(guild_id, ch_id)
        
        return {
            "success": True,
            "message": f"Cleared {queues_cleared} queue(s) for guild {guild_id}"
        }
    
    async def disconnect_from_voice(self, guild_id, channel_id=None, preserve_queue=True):
        """Disconnect from voice channel with option to clear the queue"""
        if channel_id:
            # Disconnect from a specific channel
            queue_id = self.get_queue_id(guild_id, channel_id)
            
            if queue_id in self.voice_connections and self.voice_connections[queue_id].is_connected():
                # If preserving queue and there's a current track, save it
                if preserve_queue and queue_id in self.currently_playing:
                    current_track = self.currently_playing.get(queue_id)
                    if current_track:
                        # Add current track back to the front of the queue
                        self.music_queues[queue_id].insert(0, current_track)
                else:
                    # If not preserving queue, clear it
                    self.music_queues[queue_id] = []
                
                # Always clear the currently playing track
                self.currently_playing.pop(queue_id, None)
                
                await self.voice_connections[queue_id].disconnect(force=True)
                self.voice_connections.pop(queue_id, None)
                
                message = "Disconnected from voice channel"
                if not preserve_queue:
                    message += " and cleared queue"
                
                return {"success": True, "message": message}
            else:
                return {"success": False, "message": f"Not connected to voice channel {channel_id} in guild {guild_id}"}
        
        # If no specific channel_id, disconnect from any voice connection in this guild
        for queue_id, voice_client in list(self.voice_connections.items()):
            if queue_id.startswith(f"{guild_id}_") and voice_client.is_connected():
                # Extract channel_id from queue_id
                disconnected_channel_id = queue_id.split('_')[1]
                
                # If preserving queue and there's a current track, save it
                if preserve_queue and queue_id in self.currently_playing:
                    current_track = self.currently_playing.get(queue_id)
                    if current_track:
                        # Add current track back to the front of the queue
                        self.music_queues[queue_id].insert(0, current_track)
                else:
                    # If not preserving queue, clear it
                    self.music_queues[queue_id] = []
                
                # Always clear the currently playing track
                self.currently_playing.pop(queue_id, None)
                
                await voice_client.disconnect(force=True)
                self.voice_connections.pop(queue_id, None)
                
                message = "Disconnected from voice channel"
                if not preserve_queue:
                    message += " and cleared queue"
                
                await self.update_control_panel(guild_id, disconnected_channel_id)
                
                return {"success": True, "message": message}
        
        return {"success": False, "message": "Not connected to any voice channel in this guild"}
    
    # DISCORD UI METHODS
    
    async def join_and_show_controls(self, text_channel, voice_channel, guild_id):
        """Join a voice channel and show controls in the text channel"""
        try:
            # Check if we're already in this voice channel
            queue_id = self.get_queue_id(str(guild_id), str(voice_channel.id))
            
            # If already connected to a different channel, disconnect first
            for existing_queue_id, voice_client in list(self.voice_connections.items()):
                if existing_queue_id.startswith(f"{guild_id}_") and voice_client.is_connected():
                    # Preserve queue if we're moving channels
                    if existing_queue_id != queue_id and queue_id in self.currently_playing:
                        current_track = self.currently_playing.get(queue_id)
                        if current_track:
                            self.music_queues[queue_id].insert(0, current_track)
                    
                    await voice_client.disconnect(force=True)
                    self.voice_connections.pop(existing_queue_id, None)
                    break
            
            # Join the voice channel if not already connected
            if queue_id not in self.voice_connections or not self.voice_connections[queue_id].is_connected():
                voice_client = await voice_channel.connect()
                self.voice_connections[queue_id] = voice_client
                await text_channel.send(f"Joined **{voice_channel.name}**", delete_after=10)
            
            # Create and send control panel
            await self.send_control_panel(text_channel, voice_channel, guild_id)
            
        except Exception as e:
            print(f"Error joining voice channel: {e}")
            await text_channel.send(f"Error: {str(e)}", delete_after=10)
    
    async def send_control_panel(self, text_channel, voice_channel, guild_id):
        """Send a control panel with buttons to the text channel"""
        queue_id = self.get_queue_id(str(guild_id), str(voice_channel.id))
        
        # Create embed for the control panel
        embed = discord.Embed(
            title="🎵 Music Control Panel",
            description=f"Connected to **{voice_channel.name}**",
            color=discord.Color.blurple()
        )
        
        # Add queue info if there are songs
        if self.music_queues[queue_id]:
            queue_text = "\n".join(
                f"{i+1}. {track['title']}" 
                for i, track in enumerate(self.music_queues[queue_id][:5])
            )
            if len(self.music_queues[queue_id]) > 5:
                queue_text += f"\n... and {len(self.music_queues[queue_id]) - 5} more"
            embed.add_field(name="Queue", value=queue_text or "Empty", inline=False)
        else:
            embed.add_field(name="Queue", value="Empty", inline=False)
        
        # Add currently playing info
        current_track = self.currently_playing.get(queue_id)
        if current_track:
            embed.add_field(
                name="Now Playing",
                value=f"[{current_track['title']}](https://www.youtube.com/watch?v={current_track['id']})",
                inline=False
            )
        
        # Create view with buttons
        view = MusicControlView(self, str(guild_id), str(voice_channel.id))
        
        # Send or update the control panel
        if text_channel.id in self.control_panels:
            try:
                # Try to edit existing message
                existing_message = await text_channel.fetch_message(self.control_panels[text_channel.id])
                await existing_message.edit(embed=embed, view=view)
                return
            except (discord.NotFound, discord.HTTPException):
                # Message doesn't exist anymore, send a new one
                pass
        
        # Send new control panel
        message = await text_channel.send(embed=embed, view=view)
        self.control_panels[text_channel.id] = message.id
    
    async def update_control_panel(self, guild_id, channel_id):
        """Update all control panels for a guild/channel"""
        queue_id = self.get_queue_id(guild_id, channel_id)
        
        # Find text channels with control panels for this guild
        guild = self.get_guild(int(guild_id))
        if not guild:
            return
        
        # Update all control panels in this guild
        for text_channel_id, message_id in list(self.control_panels.items()):
            try:
                text_channel = guild.get_channel(text_channel_id)
                if not text_channel:
                    continue
                
                voice_channel = guild.get_channel(int(channel_id))
                if not voice_channel:
                    continue
                
                # Update the control panel
                await self.send_control_panel(text_channel, voice_channel, guild_id)
            except Exception as e:
                print(f"Error updating control panel: {e}")
    
    # PLAYBACK METHODS
    
    async def play_next(self, guild_id, channel_id):
        """Play the next song in the queue"""
        queue_id = self.get_queue_id(guild_id, channel_id)
        print(f"play_next called for queue {queue_id}")
        
        # Check if there are songs in the queue
        if not self.music_queues[queue_id]:
            self.currently_playing.pop(queue_id, None)
            print(f"No songs in queue {queue_id}, stopping playback")
            
            # Update control panels to show empty queue
            await self.update_control_panel(guild_id, channel_id)
            return
        
        # Get guild and voice client
        voice_client, queue_id = await self.get_voice_client(guild_id, channel_id, connect=True)
        if not voice_client:
            print(f"Could not connect to voice channel {channel_id} in guild {guild_id}")
            return
        
        # Get next song
        song = self.music_queues[queue_id].pop(0)
        self.currently_playing[queue_id] = song
        
        try:
            # Use the shared MusicService to get the audio URL
            audio_url = await music_service.extract_audio_url(song['id'])
            
            if not audio_url:
                raise Exception(f"Failed to extract audio URL for {song['id']}")
            
            # Get FFmpeg options from the service
            ffmpeg_options = music_service.get_ffmpeg_options('medium')
            
            # Create FFmpeg audio source
            audio_source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
            
            # Play the song
            voice_client.play(audio_source, after=lambda e: asyncio.run_coroutine_threadsafe(
                self.play_next(guild_id, channel_id), self.loop) if e is None else print(f'Player error: {e}'))
            
            # Set the volume to a reasonable level
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source, volume=0.5)
            print(f"Now playing: {song['title']} in guild {guild_id}")
            
            # Update control panels with now playing information
            await self.update_control_panel(guild_id, channel_id)
            
        except Exception as e:
            print(f"Error playing song: {e}")
            # Try to play the next song
            self.currently_playing.pop(queue_id, None)
            asyncio.create_task(self.play_next(guild_id, channel_id))
    
    # API SERVER HANDLERS
    
    async def start_api_server(self):
        """Start a simple web server to handle API requests from the Flask app"""
        app = web.Application()
        app.add_routes([
                web.post('/api/join', self.handle_join),
                web.get('/api/guild_count', self.handle_guild_count),
                web.get('/api/guild_ids', self.handle_guild_ids),
                # Queue management routes
                web.post('/api/add_to_queue', self.handle_add_to_queue),
                web.get('/api/get_queue', self.handle_get_queue),
                web.post('/api/skip', self.handle_skip),
                web.post('/api/pause', self.handle_pause),
                web.post('/api/resume', self.handle_resume),
                web.post('/api/disconnect', self.handle_disconnect),
                web.get('/api/get_user_voice_state', self.handle_get_user_voice_state),
                web.post('/api/clear_queue', self.handle_clear_queue),
                web.post('/api/shuffle_queue', self.handle_shuffle_queue),
                web.post('/api/reorder_queue', self.handle_reorder_queue)
        ])
        
        runner = web.AppRunner(app)
        await runner.setup()
        self.api_server = web.TCPSite(runner, '0.0.0.0', 5001)
        await self.api_server.start()
        print("API server started at http://0.0.0.0:5001")
    
    # API HANDLERS
    
    async def handle_join(self, request):
        """Handle join voice channel requests"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            preserve_queue = data.get('preserve_queue', True)
            
            if not guild_id or not channel_id:
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            # Get the guild
            guild = self.get_guild(int(guild_id))
            if not guild:
                return web.json_response({"error": "Guild not found"}, status=404)
            
            # Get the voice channel
            voice_channel = guild.get_channel(int(channel_id))
            if not voice_channel or not isinstance(voice_channel, discord.VoiceChannel):
                return web.json_response({"error": "Voice channel not found"}, status=404)
            
            # Disconnect from any existing voice channel in this guild
            await self.disconnect_from_voice(guild_id, preserve_queue=preserve_queue)
            
            # Connect to the new voice channel
            voice_client, queue_id = await self.get_voice_client(guild_id, channel_id, connect=True)
            
            if not voice_client:
                return web.json_response({"error": "Failed to connect to voice channel"}, status=500)
                
            # If there are songs in the queue and we're preserving the queue, start playback
            if preserve_queue and self.music_queues[queue_id] and queue_id not in self.currently_playing:
                asyncio.create_task(self.play_next(guild_id, channel_id))
            
            return web.json_response({
                "success": True, 
                "message": f"Joined {voice_channel.name}",
                "queue_id": queue_id
            })
            
        except Exception as e:
            print(f"Error handling join request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_guild_count(self, request):
        """Handle guild count requests"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        return web.json_response({"count": len(self.guilds)})
    
    async def handle_guild_ids(self, request):
        """Handle guild IDs requests"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        guild_ids = [str(guild.id) for guild in self.guilds]
        return web.json_response({"guild_ids": guild_ids})
    
    async def handle_add_to_queue(self, request):
        """Handle adding a track to the queue"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            video_id = data.get('video_id')
            video_title = data.get('video_title', "Unknown title")
            
            if not all([guild_id, channel_id, video_id]):
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            # Use the shared add_to_queue method
            result = await self.add_to_queue(guild_id, channel_id, video_id, video_title)
            
            if result["success"]:
                return web.json_response(result)
            else:
                return web.json_response({"error": result["message"]}, status=500)
                
        except Exception as e:
            print(f"Error handling add_to_queue request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_get_queue(self, request):
        """Return the current queue for a guild/channel"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            guild_id = request.query.get('guild_id')
            channel_id = request.query.get('channel_id')
            
            if not guild_id or not channel_id:
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            queue_id = self.get_queue_id(guild_id, channel_id)
            current_track = self.currently_playing.get(queue_id)
            
            # Check if the bot is connected to this voice channel
            voice_client, _ = await self.get_voice_client(guild_id, channel_id)
            is_connected = voice_client is not None
            
            return web.json_response({
                "queue": self.music_queues[queue_id],
                "current_track": current_track,
                "is_connected": is_connected,
                "is_playing": is_connected and voice_client.is_playing(),
                "is_paused": is_connected and voice_client.is_paused()
            })
            
        except Exception as e:
            print(f"Error handling get_queue request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_skip(self, request):
        """Handle skip track requests"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            
            if not guild_id or not channel_id:
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            # Use the shared skip method
            result = await self.skip_track(guild_id, channel_id)
            
            if result["success"]:
                return web.json_response(result)
            else:
                return web.json_response({"error": result["message"]}, status=400)
                
        except Exception as e:
            print(f"Error handling skip request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_pause(self, request):
        """Handle pause playback requests"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            
            if not guild_id or not channel_id:
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            voice_client, _ = await self.get_voice_client(guild_id, channel_id)
            
            if not voice_client:
                return web.json_response({"error": "Not connected to a voice channel"}, status=400)
            
            if voice_client.is_playing():
                voice_client.pause()
                
                # Update control panels
                await self.update_control_panel(guild_id, channel_id)
                
                return web.json_response({"success": True, "message": "Paused playback"})
            else:
                return web.json_response({"error": "Not playing"}, status=400)
                
        except Exception as e:
            print(f"Error handling pause request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_resume(self, request):
        """Handle resume playback requests"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            
            if not guild_id or not channel_id:
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            voice_client, _ = await self.get_voice_client(guild_id, channel_id)
            
            if not voice_client:
                return web.json_response({"error": "Not connected to a voice channel"}, status=400)
            
            if voice_client.is_paused():
                voice_client.resume()
                
                # Update control panels
                await self.update_control_panel(guild_id, channel_id)
                
                return web.json_response({"success": True, "message": "Resumed playback"})
            else:
                return web.json_response({"error": "Not paused"}, status=400)
                
        except Exception as e:
            print(f"Error handling resume request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_disconnect(self, request):
        """Handle disconnect from voice channel requests"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            preserve_queue = data.get('preserve_queue', True)
            
            if not guild_id:
                return web.json_response({"error": "Missing guild_id parameter"}, status=400)
            
            # Use the shared disconnect method
            result = await self.disconnect_from_voice(guild_id, channel_id, preserve_queue)
            
            if result["success"]:
                return web.json_response(result)
            else:
                return web.json_response({"error": result["message"]}, status=404)
                
        except Exception as e:
            print(f"Error handling disconnect request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_get_user_voice_state(self, request):
        """Handle requests to get a user's voice state"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            # Get parameters
            guild_id = request.query.get('guild_id')
            user_id = request.query.get('user_id')
            
            if not guild_id or not user_id:
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            # Get the guild
            guild = self.get_guild(int(guild_id))
            if not guild:
                return web.json_response({"error": "Guild not found"}, status=404)
            
            # Get the member
            try:
                member = await guild.fetch_member(int(user_id))
            except discord.NotFound:
                return web.json_response({"error": "Member not found"}, status=404)
            
            # Check if user is in a voice channel
            if not member.voice:
                return web.json_response({"voice_state": None})
            
            # Return voice state information
            voice_state = {
                "channel_id": str(member.voice.channel.id),
                "channel_name": member.voice.channel.name,
                "mute": member.voice.mute,
                "deaf": member.voice.deaf,
                "self_mute": member.voice.self_mute,
                "self_deaf": member.voice.self_deaf
            }
            
            return web.json_response({"voice_state": voice_state})
            
        except Exception as e:
            print(f"Error handling get_user_voice_state request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_clear_queue(self, request):
        """Handle requests to clear a queue"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')  # Optional
            
            if not guild_id:
                return web.json_response({"error": "Missing guild_id parameter"}, status=400)
            
            # Use the shared clear_queue method
            result = await self.clear_queue(guild_id, channel_id)
            
            return web.json_response(result)
            
        except Exception as e:
            print(f"Error handling clear_queue request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_shuffle_queue(self, request):
        """Handle requests to shuffle the queue"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            
            if not guild_id or not channel_id:
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            # Use the shared shuffle method
            result = await self.shuffle_queue(guild_id, channel_id)
            
            if result["success"]:
                return web.json_response(result)
            else:
                return web.json_response({"error": result["message"]}, status=400)
                
        except Exception as e:
            print(f"Error handling shuffle_queue request: {e}")
            return web.json_response({"error": str(e)}, status=500)
    
    async def handle_reorder_queue(self, request):
        """Handle requests to reorder tracks in the queue"""
        # Check authorization
        if request.headers.get('Authorization') != f'Bearer {IPC_SECRET_KEY}':
            return web.json_response({"error": "Unauthorized"}, status=401)
        
        try:
            data = await request.json()
            guild_id = data.get('guild_id')
            channel_id = data.get('channel_id')
            old_index = data.get('old_index')
            new_index = data.get('new_index')
            
            if not all([guild_id, channel_id, old_index is not None, new_index is not None]):
                return web.json_response({"error": "Missing parameters"}, status=400)
            
            # Use the shared reorder method
            result = await self.reorder_queue(guild_id, channel_id, old_index, new_index)
            
            if result["success"]:
                return web.json_response(result)
            else:
                return web.json_response({"error": result["message"]}, status=400)
                
        except Exception as e:
            print(f"Error handling reorder_queue request: {e}")
            return web.json_response({"error": str(e)}, status=500)

# BOT COMMANDS

# Create the bot instance
bot = MyBot(command_prefix="jbot ", intents=intents)

@bot.command(name="hello")
async def hello(ctx):
    """Simple hello command to test the bot is working"""
    await ctx.send("Hello there!", delete_after=10)

@bot.command(name="jhelp")
async def help_command(ctx):
    """Show the help information for the bot"""
    embed = discord.Embed(
        title="JBot Music Commands",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="jbot", value="Type this in chat to summon the music control panel", inline=False)
    embed.add_field(name="jbot search <query>", value="Search for a YouTube video and add it to queue", inline=False)
    embed.add_field(name="jbot hello", value="Say hello to the bot", inline=False)
    
    await ctx.send(embed=embed, delete_after=10)

# Search command using the optimized bot structure
@bot.command(name='search')
async def search_command(ctx, *, query):
    """Search for a YouTube video and add it to the queue"""
    # Check if user is in a voice channel
    if not ctx.author.voice:
        await ctx.send("You need to be in a voice channel to use this command", delete_after=10)
        return
    
    # Validate query length
    if len(query.strip()) < 2:
        await ctx.send("Please provide a more specific search query (at least 2 characters)", delete_after=10)
        return
    
    voice_channel = ctx.author.voice.channel
    guild_id = str(ctx.guild.id)
    channel_id = str(voice_channel.id)
    
    # Try to search for the video using the shared service
    try:
        # Use the shared MusicService for optimized search
        results = await music_service.search_videos(query)
        
        if not results:
            await ctx.send(f"No results found for: {query}", delete_after=10)
            return
        
        # Create embed for results
        embed = discord.Embed(
            title=f"Search Results for: {query}",
            description="Select a track to play",
            color=discord.Color.green()
        )
        
        # Create dropdown menu for selecting tracks
        select = discord.ui.Select(
            placeholder="Choose a track",
            min_values=1,
            max_values=1,
            custom_id="search_results"
        )
        
        # Add options to select menu
        for i, result in enumerate(results):
            # Truncate title to fit Discord's label requirements
            def truncate_title(title, max_length=90):
                """Truncate title while preserving meaning"""
                if len(title) <= max_length:
                    return title
                return title[:max_length-3] + "..."
            
            # Sanitize title for label
            safe_title = truncate_title(result['title'])
            
            # Get duration
            duration = result.get('duration')
            if duration:
                minutes, seconds = divmod(duration, 60)
                duration_str = f"{minutes}:{seconds:02d}"
            else:
                duration_str = "Unknown"
            
            # Add to embed
            embed.add_field(
                name=f"{i+1}. {safe_title}",
                value=f"Duration: {duration_str}",
                inline=False
            )
            
            # Add to select menu
            select.add_option(
                label=f"{i+1}. {safe_title}",
                value=f"{result['id']}",
                description=f"Duration: {duration_str}"[:100]  # Description max length is 100
            )
        
        # Create view and add select
        view = discord.ui.View(timeout=60)
        view.add_item(select)
        
        # Define select callback
        async def select_callback(interaction):
            # Ensure the user who invoked the command is making the selection
            if interaction.user != ctx.author:
                await interaction.response.send_message(
                    "Only the person who used the search command can select a track.",
                    ephemeral=True
                )
                return
            
            # Get the selected track ID
            video_id = interaction.data['values'][0]
            
            # Find the selected track in the results
            selected_track = None
            for result in results:
                if result['id'] == video_id:
                    selected_track = result
                    break
            
            if not selected_track:
                await interaction.response.send_message(
                    "Error: Could not find the selected track.",
                    ephemeral=True
                )
                return
            
            # Acknowledge the interaction
            await interaction.response.defer(ephemeral=True)
            
            # Use the shared add_to_queue method
            result = await bot.add_to_queue(
                guild_id, 
                channel_id, 
                selected_track['id'], 
                selected_track['title']
            )
            
            # Confirm selection
            await interaction.followup.send(
                f"Added to queue: **{selected_track['title']}**",
                ephemeral=True
            )
        
        # Assign callback
        select.callback = select_callback
        
        # Send results
        await ctx.send(embed=embed, view=view, delete_after=10)
        
    except Exception as e:
        print(f"Error searching for videos: {e}")
        await ctx.send(f"An error occurred while searching: {str(e)}", delete_after=10)

if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)