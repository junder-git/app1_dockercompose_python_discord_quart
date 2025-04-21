"""
hello command for Discord bot
Simple hello command to test that the bot is working
"""

async def hello(ctx):
    """
    Simple hello command to test the bot is working
    
    Args:
        ctx: Command context
    """
    # Get cleartimer from bot or default to 10 seconds
    cleartimer = getattr(ctx.bot, 'cleartimer', 10)
    await ctx.send("Hello there!", delete_after=cleartimer)