"""
join_and_show_controls method for Discord bot
Joins a voice channel and shows music controls in a text channel
"""

async def join_and_show_controls(self, text_channel, voice_channel, guild_id):
    """
    Join a voice channel and show controls in the text channel
    
    Args:
        text_channel: Discord text channel to send controls to
        voice_channel: Discord voice channel to join
        guild_id: ID of the Discord guild
    """
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
            
            # Get cleartimer or default to 10 seconds
            cleartimer = getattr(self, 'cleartimer', 10)
            await text_channel.send(f"Joined **{voice_channel.name}**", delete_after=cleartimer)
        
        # Create and send control panel
        await self.send_control_panel(text_channel, voice_channel, guild_id)
        
    except Exception as e:
        print(f"Error joining voice channel: {e}")
        # Get cleartimer or default to 10 seconds
        cleartimer = getattr(self, 'cleartimer', 10)
        await text_channel.send(f"Error: {str(e)}", delete_after=cleartimer)