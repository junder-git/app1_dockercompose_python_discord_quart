"""
Voice Blueprint for Discord Bot
Handles voice channel connections
"""
import types
import discord
import asyncio

def apply(bot):
    """
    Apply voice blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Bind voice methods to the bot
    bot.get_voice_client = types.MethodType(get_voice_client, bot)
    bot.disconnect_from_voice = types.MethodType(disconnect_from_voice, bot)
    bot.follow_to_voice_channel = types.MethodType(follow_to_voice_channel, bot)
    bot.check_same_voice_channel = types.MethodType(check_same_voice_channel, bot)

async def get_voice_client(self, guild_id, channel_id, connect=False):
    """
    Get or create a voice client for the specified channel
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
        connect (bool, optional): Whether to connect if not already connected
        
    Returns:
        tuple: (voice_client, queue_id) tuple
    """
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

async def disconnect_from_voice(self, guild_id, channel_id=None, preserve_queue=True):
    """
    Disconnect from voice channel with option to clear the queue
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str, optional): Discord channel ID. If not provided, disconnects from all channels in the guild.
        preserve_queue (bool, optional): Whether to preserve the queue after disconnecting
        
    Returns:
        dict: Result containing success status and message
    """
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

async def follow_to_voice_channel(self, guild_id, current_channel_id, new_channel_id, user):
    """
    Follow a user to a new voice channel, preserving the queue and current track
    
    Args:
        guild_id (str): Discord guild ID
        current_channel_id (str): Current voice channel ID
        new_channel_id (str): New voice channel ID to move to
        user: Discord user object
        
    Returns:
        dict: Result containing success status and message
    """
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
                    await self.update_control_panel(guild_id, new_channel_id)
            except Exception as e:
                print(f"Error updating control panel: {e}")
        
        return {
            "success": True,
            "message": f"Followed {user.display_name} to {new_voice_channel.name}"
        }
        
    except Exception as e:
        print(f"Error following to voice channel: {e}")
        return {"success": False, "message": f"Error: {str(e)}"}

async def check_same_voice_channel(self, user, channel_id):
    """
    Check if a user is in the specified voice channel
    
    Args:
        user: Discord user object
        channel_id (str): Discord channel ID
        
    Returns:
        bool: True if user is in the specified channel, False otherwise
    """
    return user.voice and str(user.voice.channel.id) == channel_id

