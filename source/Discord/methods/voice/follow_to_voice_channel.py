"""
follow_to_voice_channel method for Discord bot
Follows a user to a new voice channel while preserving the queue and playback state
"""
import asyncio
import discord

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