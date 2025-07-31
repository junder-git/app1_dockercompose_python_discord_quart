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

    # 🔽 Clear globals commands cache
    try:
        print("Clearing global commands...")
        self.tree.clear_commands()
        await self.tree.sync()
        print("✅ Global commands cleared.")
    except Exception as e:
        print(f"❌ Failed to clear global commands: {e}")

    
    if len(self.tree.get_commands()) > 0:
        print("Syncing slash commands to guilds...")
        
        # Try a different approach - sync to one guild first as a test
        test_guild = self.guilds[0] if self.guilds else None
        if test_guild:
            print(f"Testing sync with guild: {test_guild.name}")
            try:
                # Clear any existing commands first
                self.tree.clear_commands(guild=test_guild)
                print("Cleared existing commands for test guild")
                
                # Copy commands to guild
                self.tree.copy_global_to(guild=test_guild)
                print("Copied global commands to test guild")
                
                # Now sync
                synced = await self.tree.sync(guild=test_guild)
                print(f"  🧪 TEST {test_guild.name}: {len(synced)} command(s)")
                for cmd in synced:
                    print(f"    - {cmd.name}")
                
                if len(synced) > 0:
                    print("✅ SUCCESS! Test sync worked. Syncing to all guilds...")
                    
                    # Now sync to all guilds
                    for guild in self.guilds[1:]:  # Skip the test guild
                        try:
                            self.tree.clear_commands(guild=guild)
                            self.tree.copy_global_to(guild=guild)
                            synced = await self.tree.sync(guild=guild)
                            print(f"  ✅ {guild.name}: {len(synced)} command(s)")
                        except Exception as e:
                            print(f"  ❌ {guild.name}: Failed - {e}")
                else:
                    print("❌ Test sync failed - trying global sync instead")
                    try:
                        synced = await self.tree.sync()
                        print(f"Global sync: {len(synced)} command(s) (will take up to 1 hour)")
                    except Exception as e:
                        print(f"Global sync failed: {e}")
                        
            except Exception as e:
                print(f"Test sync failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("Command sync process complete!")
    else:
        print("No commands found in tree - skipping sync")