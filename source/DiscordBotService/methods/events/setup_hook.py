"""
setup_hook method for Discord bot
Called when the bot starts up
"""

async def setup_hook(self):
    """
    This is called when the bot starts up
    """
    # Start the API server
    await self.start_api_server()
    print("API server started")