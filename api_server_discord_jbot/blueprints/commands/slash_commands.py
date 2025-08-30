"""
Smart slash commands for Discord bot - Clean version with fallback search
"""
import discord
import asyncio

# For registering with the bot
def apply_slash_commands(bot):
    """Apply slash commands to the bot"""
    print("Applying slash commands to bot - clean version with fallback search")
    
    # JAI command with two choices and fallback to search
    @discord.app_commands.command(name="jai", description="Music bot control - join, leave, or play music")
    @discord.app_commands.describe(action="Choose 'join'/'leave' OR type any song/artist/URL to search and play")
    @discord.app_commands.choices(action=[
        discord.app_commands.Choice(name='Join Voice Channel', value='join'),
        discord.app_commands.Choice(name='Leave Voice Channel', value='leave'),
    ])
    async def jai_command(interaction: discord.Interaction, action: str):
        """JAI command - handles choices or treats unknown input as search query"""
        print(f"JAI command called by {interaction.user} with action: {action}")
        
        # Check if user is in a voice channel (required for all operations)
        if not interaction.user.voice:
            await interaction.response.send_message(
                "❌ You need to be in a voice channel to use JAI.", 
                ephemeral=True
            )
            return
        
        # Defer the response to avoid timeout
        await interaction.response.defer(ephemeral=True)
        
        user_voice_channel = interaction.user.voice.channel
        action_lower = action.lower().strip()
        
        try:
            # Check if bot is currently connected to a voice channel in this guild
            voice_client = discord.utils.get(bot.voice_clients, guild=interaction.guild)
            is_connected = voice_client and voice_client.is_connected()
            
            if action_lower == "join":
                # JOIN ACTION
                if is_connected:
                    await interaction.followup.send(
                        f"❌ I'm already connected to **{voice_client.channel.name}**. Use 'Leave Voice Channel' first.",
                        ephemeral=True
                    )
                    return
                
                await join_and_show_controls(bot, interaction, user_voice_channel)
                
            elif action_lower == "leave":
                # LEAVE ACTION
                if not is_connected:
                    await interaction.followup.send(
                        "❌ I'm not currently connected to any voice channel.",
                        ephemeral=True
                    )
                    return
                
                # Check if user is in the same voice channel
                if interaction.user.voice.channel != voice_client.channel:
                    await interaction.followup.send(
                        f"❌ I'm connected to **{voice_client.channel.name}**. Join that channel to make me leave.",
                        ephemeral=True
                    )
                    return
                
                await leave_voice_channel(bot, interaction, voice_client)
            
        except Exception as e:
            print(f"Error in JAI command: {e}")
            import traceback
            traceback.print_exc()
            await interaction.followup.send(
                f"❌ An error occurred: {str(e)}",
                ephemeral=True
            )
    
    # Add the command to the tree
    bot.tree.add_command(jai_command)
    print("JAI command added to tree successfully")

"""
Function to join a voice channel and show controls
"""

async def join_and_show_controls(self, text_channel, voice_channel, guild_id=discord.Interaction.guild.id):
    """
    Join a voice channel and show controls in the text channel
    
    Args:
        text_channel: Discord text channel to send controls to
        voice_channel: Discord voice channel to join
        guild_id: ID of the Discord guild
    """
    try:
        # Check if we're already in this voice channel
        queue_id = self.get_queue_id(str(guild_id), str(voice_channel.id))
        
        # If already connected to a different channel, disconnect first
        for existing_queue_id, voice_client in list(self.voice_connections.items()):
            if existing_queue_id.startswith(f"{guild_id}_") and voice_client.is_connected():
                # Preserve queue if we're moving channels
                if existing_queue_id != queue_id and queue_id in self.currently_playing:
                    current_track = self.currently_playing.get(queue_id)
                    if current_track:
                        self.music_queues[queue_id].insert(0, current_track)
                
                await voice_client.disconnect(force=True)
                self.voice_connections.pop(existing_queue_id, None)
                break
        
        # Join the voice channel if not already connected
        if queue_id not in self.voice_connections or not self.voice_connections[queue_id].is_connected():
            voice_client = await voice_channel.connect()
            self.voice_connections[queue_id] = voice_client
            
            # Get cleartimer or default to 10 seconds
            cleartimer = getattr(self, 'cleartimer', 10)
            
            # Send confirmation message to the original text channel
            join_message = await text_channel.send(f"🎵 Joined **{voice_channel.name}** and posted controls!")
            await join_message.delete(delay=cleartimer)
        
        # Create and send control panel
        await self.send_control_panel(text_channel, voice_channel, str(guild_id))
        
    except Exception as e:
        print(f"Error joining voice channel: {e}")
        # Get cleartimer or default to 10 seconds
        cleartimer = getattr(self, 'cleartimer', 10)
        error_message = await text_channel.send(f"❌ Error: {str(e)}")
        await error_message.delete(delay=cleartimer)

async def leave_voice_channel(bot, interaction, voice_client):
    """Leave the voice channel"""
    try:
        channel_id = str(voice_client.channel.id)
        voice_channel_name = voice_client.channel.name
        
        # Disconnect from voice channel
        from .leave import disconnect_from_voice
        await disconnect_from_voice(bot, str(interaction.guild.id), channel_id, preserve_queue=False)
        
        await interaction.followup.send(
            f"{interaction.user.mention} ✅ Left **{voice_channel_name}** and cleared the queue.",
            ephemeral=True
        )
        
    except Exception as e:
        print(f"Error in leave_voice_channel: {e}")
        import traceback
        traceback.print_exc()

async def countdown_and_cleanup(message, seconds):
    """Show countdown and then delete the message - fixed for webhook messages"""
    try:
        # Get the original content and view (handle webhook messages)
        original_content = message.content
        original_view = getattr(message, 'view', None)
        
        # Countdown
        for remaining in range(seconds, 0, -1):
            await asyncio.sleep(1)
            try:
                # Update message with countdown
                countdown_content = f"{original_content}\n\n*This message will disappear in {remaining} second{'s' if remaining != 1 else ''}...*"
                if original_view:
                    await message.edit(content=countdown_content, view=original_view)
                else:
                    await message.edit(content=countdown_content)
            except discord.NotFound:
                # Message was already deleted
                return
            except discord.HTTPException:
                # Error editing message, continue countdown
                continue
        
        # Delete the message
        try:
            await message.delete()
        except discord.NotFound:
            # Message was already deleted
            pass
        except discord.HTTPException:
            # Can't delete the message, try to disable view
            try:
                if original_view:
                    await message.edit(view=None)
            except:
                pass
                
    except Exception as e:
        print(f"Error in countdown_and_cleanup: {e}")

async def get_or_create_jai_channel(guild):
    """Find or create the jai text channel"""
    # First, try to find existing "jai" channel
    for channel in guild.text_channels:
        if channel.name.lower() == "jai":
            return channel
    
    # If no "jai" channel exists, create one
    try:
        jai_channel = await guild.create_text_channel(
            name="jai",
            topic="🎵 JAI Music Bot Control Panel",
            reason="Created by JAI music bot"
        )
        
        # Send welcome message to new channel
        welcome_embed = discord.Embed(
            title="🎵 Welcome to JAI Music Bot!",
            description="This channel has been created for music controls.\n\nUse `/jai` to get started!",
            color=discord.Color.green()
        )
        await jai_channel.send(embed=welcome_embed)
        
        return jai_channel
        
    except discord.Forbidden:
        return None
    except Exception as e:
        print(f"Error creating jai channel: {e}")
        return None