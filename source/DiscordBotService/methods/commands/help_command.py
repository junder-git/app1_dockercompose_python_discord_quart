"""
help_command for Discord bot
Shows help information about available commands
"""
import discord

async def help_command(ctx):
    """
    Show the help information for the bot
    
    Args:
        ctx: Command context
    """
    embed = discord.Embed(
        title="JBot Music Commands",
        description="Here are the available commands:",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="jbot", value="Type this in chat to summon the music control panel", inline=False)
    embed.add_field(name="jbot search <query>", value="Search for a YouTube video and add it to queue", inline=False)
    embed.add_field(name="jbot hello", value="Say hello to the bot", inline=False)
    
    # Get cleartimer from bot or default to 10 seconds
    cleartimer = getattr(ctx.bot, 'cleartimer', 10)
    await ctx.send(embed=embed, delete_after=cleartimer)