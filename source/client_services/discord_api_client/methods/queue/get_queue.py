"""
Method to get the current queue for a guild
"""

async def get_queue(self, guild_id, channel_id=None):
    """
    Get the current queue for a guild
    
    Args:
        guild_id (str): Discord guild ID
        channel_id (str, optional): Discord channel ID
        
    Returns:
        dict: Queue information
    """
    params = {"guild_id": guild_id}
    if channel_id:
        params["channel_id"] = channel_id
        
    default_response = {
        "queue": [], 
        "current_track": None,
        "is_connected": False,
        "is_playing": False,
        "is_paused": False
    }
    
    result = await self._get_request("get_queue", params, default_response)
    
    # Ensure we have all the required fields with defaults
    if "queue" not in result:
        result["queue"] = []
    if "current_track" not in result:
        result["current_track"] = None
    if "is_connected" not in result:
        # Infer connection status from the current track
        result["is_connected"] = result.get("current_track") is not None
    if "is_playing" not in result:
        # Infer playing status
        result["is_playing"] = result.get("current_track") is not None
    if "is_paused" not in result:
        result["is_paused"] = False
        
    return result