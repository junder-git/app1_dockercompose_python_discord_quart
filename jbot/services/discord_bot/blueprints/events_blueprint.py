"""
Events Blueprint for Discord Bot
Handles Discord event callbacks
"""
import types

def apply(bot):
    """
    Apply events blueprint functionality to the bot
    
    Args:
        bot: The Discord bot instance
    """
    # Register event handlers
    bot.on_ready = types.MethodType(on_ready, bot)

async def on_ready(self):
    """Called when the bot has connected to Discord"""
    print(f"Bot is ready as {self.user.name} ({self.user.id})")
    
    # Print all guilds the bot is in
    print(f"Bot is in {len(self.guilds)} guilds:")
    for guild in self.guilds:
        print(f"  • {guild.name} (ID: {guild.id})")