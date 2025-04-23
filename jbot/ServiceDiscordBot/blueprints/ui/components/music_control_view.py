"""
Music Control View for Discord bot (updated to use command functions)
"""
import discord
from ...commands.join import check_same_voice_channel, follow_to_voice_channel
from ...commands.leave import disconnect_from_voice
from ...commands.skip import skip_track
from ...commands.stop import stop_playback
from ...commands.pause import toggle_playback
from ...commands.queue import shuffle_queue
from ..modals.search_modal import SearchModal
from ..modals.enhanced_url_modal import EnhancedURLModal
from ..helpers.playlist_help import show_playlist_help

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
            url="https://music.junder.uk",
            row=2
        )
        self.add_item(web_player_button)

    @discord.ui.button(label="Search", style=discord.ButtonStyle.secondary, emoji="🔍", custom_id="search", row=2)
    async def search_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Send the search modal
        await interaction.response.send_modal(SearchModal(self.bot, self.guild_id, self.channel_id))
    
    @discord.ui.button(label="Add URL", style=discord.ButtonStyle.secondary, emoji="🔗", custom_id="add_url", row=2)
    async def add_url_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Send the enhanced URL modal
        await interaction.response.send_modal(EnhancedURLModal(self.bot, self.guild_id, self.channel_id))
    
    @discord.ui.button(label="?", style=discord.ButtonStyle.secondary, emoji="❓", custom_id="playlist_help", row=2)
    async def playlist_help_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await show_playlist_help(interaction)
    
    @discord.ui.button(label="Play/Pause", style=discord.ButtonStyle.primary, emoji="⏯️", custom_id="play_pause")
    async def play_pause_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await check_same_voice_channel(self.bot, interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Use the shared toggle play/pause method
        result = await toggle_playback(self.bot, self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)
        
        # Update the control panel
        await self.bot.update_control_panel(self.guild_id, self.channel_id)
    
    @discord.ui.button(label="Skip", style=discord.ButtonStyle.primary, emoji="⏭️", custom_id="skip")
    async def skip_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await check_same_voice_channel(self.bot, interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Use the shared skip method
        result = await skip_track(self.bot, self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)
    
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger, emoji="⏹️", custom_id="stop")
    async def stop_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await check_same_voice_channel(self.bot, interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Set the interruption flag for any ongoing playlist additions
        queue_id = self.bot.get_queue_id(self.guild_id, self.channel_id)
        self.bot.playlist_processing[queue_id] = True
        
        # Use the shared stop method
        result = await stop_playback(self.bot, self.guild_id, self.channel_id)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)
        
        # Update the control panel
        await self.bot.update_control_panel(self.guild_id, self.channel_id)
    
    @discord.ui.button(label="Shuffle", style=discord.ButtonStyle.secondary, emoji="🔀", custom_id="shuffle", row=1)
    async def shuffle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await check_same_voice_channel(self.bot, interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Use the shared shuffle method
        result = await shuffle_queue(self.bot, self.guild_id, self.channel_id)
        
        # Send response that will auto-delete after 10 seconds
        message = await interaction.followup.send(result["message"])
        await message.delete(delay=10)
        
        # Update the control panel to show the new queue order
        await self.bot.update_control_panel(self.guild_id, self.channel_id)

    @discord.ui.button(label="Follow VC", style=discord.ButtonStyle.secondary, emoji="👣", custom_id="follow_vc", row=1)
    async def follow_vc_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in a voice channel, but not necessarily the same one
        if not interaction.user.voice:
            message = await interaction.followup.send("You need to be in a voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Get the user's current voice channel
        new_voice_channel = interaction.user.voice.channel
        
        # If user is already in the same voice channel as the bot, no need to move
        if str(new_voice_channel.id) == self.channel_id:
            message = await interaction.followup.send("I'm already in your voice channel!", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Use the shared follow voice channel method
        result = await follow_to_voice_channel(
            self.bot,
            self.guild_id,
            self.channel_id,  # Current voice channel
            str(new_voice_channel.id),  # New voice channel
            interaction.user
        )
        
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)

    @discord.ui.button(label="Disconnect", style=discord.ButtonStyle.secondary, emoji="👋", custom_id="disconnect", row=1)
    async def disconnect_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Check if user is in the same voice channel
        if not await check_same_voice_channel(self.bot, interaction.user, self.channel_id):
            message = await interaction.followup.send("You need to be in the same voice channel to use this control.", ephemeral=True)
            await message.delete(delay=10)
            return
        
        # Set the interruption flag for any ongoing playlist additions
        queue_id = self.bot.get_queue_id(self.guild_id, self.channel_id)
        self.bot.playlist_processing[queue_id] = True
        
        # Use the shared disconnect method
        result = await disconnect_from_voice(self.bot, self.guild_id, self.channel_id, preserve_queue=True)
        message = await interaction.followup.send(result["message"], ephemeral=True)
        await message.delete(delay=10)
        
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