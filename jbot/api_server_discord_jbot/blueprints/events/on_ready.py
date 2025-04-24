"""
Handler for bot ready event
"""

async def on_ready(self):
    """
    Called when the bot has connected to Discord
    """
    print(f"Bot is ready as {self.user.name} ({self.user.id})")
    
    # Print all guilds the bot is in
    print(f"Bot is in {len(self.guilds)} guilds:")
    for guild in self.guilds:
        print(f"  • {guild.name} (ID: {guild.id})")