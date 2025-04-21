"""
get_voice_client method for Discord bot
Gets or creates a voice client for a specified channel
"""
import discord

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