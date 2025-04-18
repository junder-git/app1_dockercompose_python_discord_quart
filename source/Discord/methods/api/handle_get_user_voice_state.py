"""
handle_get_user_voice_state method for Discord bot
Handles API requests to get a user's voice state
"""
from aiohttp import web
import discord

async def handle_get_user_voice_state(self, request):
    """
    Handle requests to get a user's voice state
    
    Args:
        request: The HTTP request object
        
    Returns:
        web.Response: JSON response with voice state information
    """
    # Check authorization
    if request.headers.get('Authorization') != f'Bearer {self.SECRET_KEY}':
        return web.json_response({"error": "Unauthorized"}, status=401)
    
    try:
        # Get parameters
        guild_id = request.query.get('guild_id')
        user_id = request.query.get('user_id')
        
        if not guild_id or not user_id:
            return web.json_response({"error": "Missing parameters"}, status=400)
        
        # Get the guild
        guild = self.get_guild(int(guild_id))
        if not guild:
            return web.json_response({"error": "Guild not found"}, status=404)
        
        # Get the member
        try:
            member = await guild.fetch_member(int(user_id))
        except discord.NotFound:
            return web.json_response({"error": "Member not found"}, status=404)
        
        # Check if user is in a voice channel
        if not member.voice:
            return web.json_response({"voice_state": None})
        
        # Return voice state information
        voice_state = {
            "channel_id": str(member.voice.channel.id),
            "channel_name": member.voice.channel.name,
            "mute": member.voice.mute,
            "deaf": member.voice.deaf,
            "self_mute": member.voice.self_mute,
            "self_deaf": member.voice.self_deaf
        }
        
        return web.json_response({"voice_state": voice_state})
        
    except Exception as e:
        print(f"Error handling get_user_voice_state request: {e}")
        return web.json_response({"error": str(e)}, status=500)