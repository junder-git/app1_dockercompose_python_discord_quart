"""
Function to send a control panel to a text channel
"""
import discord
from .components.music_control_view import MusicControlView

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