"""
on_ready method for Discord bot
Called upon the READY event when the bot connects to Discord
"""

async def on_ready(self):
    """
    Called upon the READY event
    """
    print("Bot is ready.")
    print(f"Logged in as {self.user.name} ({self.user.id})")
    
    # Print all guilds the bot is in
    print("Bot is in the following guilds:")
    for guild in self.guilds:
        print(f"- {guild.name} (ID: {guild.id})")