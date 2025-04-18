"""
on_message method for Discord bot
Handles incoming Discord messages
"""

async def on_message(self, message):
    """
    Handle incoming messages
    
    Args:
        message: The Discord message object
    """
    # Don't respond to own messages
    if message.author == self.user:
        return
    
    # Process commands first
    await self.process_commands(message)
    
    # Check for the "jbot" trigger word
    if message.content.lower() == "jbot":
        # Check if the user is in a voice channel
        if message.author.voice and message.author.voice.channel:
            voice_channel = message.author.voice.channel
            
            # Create a response with UI controls
            await self.join_and_show_controls(message.channel, voice_channel, message.guild.id)
        else:
            # Clear timer usually defined at module level, assume 10 seconds if not found
            cleartimer = getattr(self, 'cleartimer', 10)
            await message.channel.send("You need to be in a voice channel first!", delete_after=cleartimer)