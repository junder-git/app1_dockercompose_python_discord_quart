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
    
    # Check if we have commands to sync
    print(f"Commands available for sync: {len(self.tree.get_commands())}")
    for cmd in self.tree.get_commands():
        print(f"  - {cmd.name}: {cmd.description}")
    
    if len(self.tree.get_commands()) > 0:
        print("Syncing slash commands to guilds...")
        success_count = 0
        for guild in self.guilds:
            try:
                synced = await self.tree.sync(guild=guild)
                print(f"  ✅ {guild.name}: {len(synced)} command(s)")
                for cmd in synced:
                    print(f"    - {cmd.name}")
                success_count += 1
            except Exception as e:
                print(f"  ❌ {guild.name}: Failed to sync - {e}")
        
        print(f"Guild slash command sync complete! Synced to {success_count}/{len(self.guilds)} guilds.")
        print("Commands should appear immediately in Discord!")
    else:
        print("No commands found in tree - skipping sync")