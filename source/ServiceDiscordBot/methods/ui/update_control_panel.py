"""
update_control_panel method for Discord bot
Updates all control panels for a guild/channel
"""

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