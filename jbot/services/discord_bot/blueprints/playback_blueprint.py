"""
Playback Blueprint for Discord Bot
Handles music playback controls
"""
import types
import asyncio
import discord

def apply(bot):
    """
    Apply playback blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Bind playback methods to the bot
    bot.play_next = types.MethodType(play_next, bot)
    bot.skip_track = types.MethodType(skip_track, bot)
    bot.toggle_playback = types.MethodType(toggle_playback, bot)
    bot.stop_playback = types.MethodType(stop_playback, bot)

async def play_next(self, guild_id, channel_id):
    """
    Play the next song in the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
    """
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
        # Use the music client to get the audio URL
        audio_url = await self.music_client.extract_audio_url(song['id'])
        
        if not audio_url:
            raise Exception(f"Failed to extract audio URL for {song['id']}")
        
        # Get FFmpeg options from the service
        ffmpeg_options = self.music_client.get_ffmpeg_options('medium')
        
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

async def skip_track(self, guild_id, channel_id):
    """
    Skip the current track
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result containing success status and message
    """
    voice_client, queue_id = await self.get_voice_client(guild_id, channel_id)
    
    if not voice_client:
        return {"success": False, "message": "Not connected to a voice channel"}
    
    if voice_client.is_playing() or voice_client.is_paused():
        voice_client.stop()
        return {"success": True, "message": "⏭️ Skipped to next track"}
    else:
        return {"success": False, "message": "Nothing is playing to skip"}

async def toggle_playback(self, guild_id, channel_id):
    """
    Toggle play/pause state for a voice client
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result containing success status and message
    """
    voice_client, queue_id = await self.get_voice_client(guild_id, channel_id)
    
    if not voice_client:
        return {"success": False, "message": "Not connected to a voice channel"}
    
    if voice_client.is_paused():
        voice_client.resume()
        await self.update_control_panel(guild_id, channel_id)
        return {"success": True, "message": "▶️ Resumed playback"}
    
    elif voice_client.is_playing():
        voice_client.pause()
        await self.update_control_panel(guild_id, channel_id)
        return {"success": True, "message": "⏸️ Paused playback"}
    
    else:
        # Not playing or paused, try to start playing if there's a queue
        if self.music_queues[queue_id]:
            asyncio.create_task(self.play_next(guild_id, channel_id))
            return {"success": True, "message": "▶️ Started playback"}
        else:
            return {"success": False, "message": "No tracks in queue to play"}

async def stop_playback(self, guild_id, channel_id):
    """
    Stop playback and clear the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        
    Returns:
        dict: Result containing success status and message
    """
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
    
    # Update control panel
    await self.update_control_panel(guild_id, channel_id)
    
    return {"success": True, "message": "⏹️ Stopped playback and cleared queue"}