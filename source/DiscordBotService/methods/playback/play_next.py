"""
play_next method for Discord bot
Plays the next song in the queue
"""
import asyncio
import discord
import os
from music_player_client import MusicService

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
        # Create music service instance if we don't already have one
        if not hasattr(self, 'music_service'):
            YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
            self.music_service = MusicService(api_key=YOUTUBE_API_KEY)
            
        # Use the shared MusicService to get the audio URL
        audio_url = await self.music_service.extract_audio_url(song['id'])
        
        if not audio_url:
            raise Exception(f"Failed to extract audio URL for {song['id']}")
        
        # Get FFmpeg options from the service
        ffmpeg_options = self.music_service.get_ffmpeg_options('medium')
        
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