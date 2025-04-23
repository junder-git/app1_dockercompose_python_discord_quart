"""
Helper function to show playlist selection help
"""
import discord

async def show_playlist_help(interaction: discord.Interaction):
    """
    Show help information about playlist selection options
    
    Args:
        interaction: Discord interaction object
    """
    embed = discord.Embed(
        title="Playlist Selection Options",
        description="When adding a playlist, you can specify which tracks to add:",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="Leave Empty",
        value="Add all tracks from the playlist",
        inline=False
    )
    
    embed.add_field(
        name="Single Number",
        value="Add only the track at that position (e.g., `5` for the 5th track)",
        inline=False
    )
    
    embed.add_field(
        name="Range",
        value="Add tracks in that range (e.g., `5-10` for tracks 5 through 10)",
        inline=False
    )
    
    embed.add_field(
        name="Comma-separated Numbers",
        value="Add specific tracks (e.g., `1,3,5,9` for tracks 1, 3, 5, and 9)",
        inline=False
    )
    
    # Add a help button to the URL modal
    view = discord.ui.View(timeout=60)
    
    # Add a link button to dismiss
    dismiss_button = discord.ui.Button(
        label="Dismiss",
        style=discord.ButtonStyle.secondary,
        custom_id="dismiss_help"
    )
    async def dismiss_callback(interaction):
        await interaction.response.defer()
        await interaction.delete_original_message()
    
    dismiss_button.callback = dismiss_callback
    view.add_item(dismiss_button)
    
    # Send the help message
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True, delete_after=10)