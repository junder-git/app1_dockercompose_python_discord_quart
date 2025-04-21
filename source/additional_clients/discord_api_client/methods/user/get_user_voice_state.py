"""
Method to get the voice state of a user in a guild
"""

async def get_user_voice_state(self, guild_id, user_id):
    """
    Get the voice state of a user in a guild
    
    Args:
        guild_id (str): Discord guild ID
        user_id (str): Discord user ID
        
    Returns:
        dict: Voice state information or None
    """
    params = {"guild_id": guild_id, "user_id": user_id}
    result = await self._get_request("get_user_voice_state", params)
    return result.get("voice_state")