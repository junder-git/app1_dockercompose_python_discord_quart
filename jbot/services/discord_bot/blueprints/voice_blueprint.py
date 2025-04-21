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
    bot.join_and_show_controls = types.MethodType(join_and_show_controls, bot)
    bot.update_control_panel = types.MethodType(update_control_panel, bot)
    bot.send_control_panel = types.MethodType(send_control_panel, bot)

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
        await self.send_control_panel(text_channel, voice_channel, str(guild_id))
        
    except Exception as e:
        print(f"Error joining voice channel: {e}")
        # Get cleartimer or default to 10 seconds
        cleartimer = getattr(self, 'cleartimer', 10)
        await text_channel.send(f"Error: {str(e)}", delete_after=cleartimer)

async def send_control_panel(self, text_channel, voice_channel, guild_id):
    """
    Send a control panel with buttons to the text channel
    
    Args:
        text_channel: Discord text channel object
        voice_channel: Discord voice channel object
        guild_id: Discord guild ID
    """
    queue_id = self.get_queue_id(guild_id, str(voice_channel.id))
    
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
    view = MusicControlView(self, guild_id, str(voice_channel.id))
    
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
    """
    Update all control panels for a guild/channel
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str): Discord channel ID
    """
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


# UI Components for Discord Buttons
class MusicControlView(discord.ui.View):
    def __init__(self, bot, guild_id, channel_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.queue_id = bot.get_queue_id(guild_id, channel_id)

        # Create a link button for web player
        web_player_button = discord.ui.Button(
            label="Web Player", 
            style=discord.ButtonStyle.link, 
            url="http://localhost",
            row=2
        )
        self.add_item(web_player_button)

    @discord.ui.button(label="Search", style=discord.ButtonStyle.secondary, emoji="🔍", custom_id="search", row=2)
    async def search_button(self, interaction, button):
        # Send search modal (implementation would be added later as needed)
        await interaction.response.send_message("Search feature coming soon...", ephemeral=True)
    
    @discord.ui.button(label="Play/Pause", style=discord.ButtonStyle.primary, emoji="⏯️", custom_id="play_pause")
    async def play_pause_button(self, interaction, button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            return
        
        # Use the shared toggle play/pause method
        result = await self.bot.toggle_playback(self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        
        # Update the control panel
        await self.bot.update_control_panel(self.guild_id, self.channel_id)
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏭️", custom_id="skip")
    async def skip_button(self, interaction, button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            return
        
        # Use the shared skip method
        result = await self.bot.skip_track(self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
    
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️", custom_id="stop")
    async def stop_button(self, interaction, button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            return
        
        # Set the interruption flag for any ongoing playlist additions
        queue_id = self.bot.get_queue_id(self.guild_id, self.channel_id)
        self.bot.playlist_processing[queue_id] = True
        
        # Use the shared stop method
        result = await self.bot.stop_playback(self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        
        # Update the control panel
        await self.bot.update_control_panel(self.guild_id, self.channel_id)
    
    @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.secondary, emoji="🔀", custom_id="shuffle", row=1)
    async def shuffle_button(self, interaction, button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            return
        
        # Use the shared shuffle method
        result = await self.bot.shuffle_queue(self.guild_id, self.channel_id)
        
        # Send response
        message = await interaction.followup.send(result["message"], ephemeral=True)
        
        # Update the control panel to show the new queue order
        await self.bot.update_control_panel(self.guild_id, self.channel_id)

    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.secondary, emoji="👋", custom_id="disconnect", row=1)
    async def disconnect_button(self, interaction, button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await self.bot.check_same_voice_channel(interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            return
        
        # Set the interruption flag for any ongoing playlist additions
        queue_id = self.bot.get_queue_id(self.guild_id, self.channel_id)
        self.bot.playlist_processing[queue_id] = True
        
        # Use the shared disconnect method
        result = await self.bot.disconnect_from_voice(self.guild_id, self.channel_id, preserve_queue=True)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        
        # Delete the control panel message
        try:
            channel = interaction.channel
            if channel.id in self.bot.control_panels:
                message_id = self.bot.control_panels[channel.id]
                message = await channel.fetch_message(message_id)
                await message.delete()
                # Remove from control panels dictionary
                self.bot.control_panels.pop(channel.id, None)
        except Exception as e:
            print(f"Error removing control panel: {e}")