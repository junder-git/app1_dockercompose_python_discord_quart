"""
disconnect_from_voice method for Discord bot
Disconnects from voice channel with option to preserve the queue
"""

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