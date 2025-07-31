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
        print("Clearing old commands and syncing new ones...")
        
        # Try a different approach - sync to one guild first as a test
        test_guild = self.guilds[0] if self.guilds else None
        if test_guild:
            print(f"Testing sync with guild: {test_guild.name}")
            try:
                # Clear any existing commands first - this removes old commands
                print("Clearing old guild commands...")
                self.tree.clear_commands(guild=test_guild)
                await self.tree.sync(guild=test_guild)  # Sync empty tree to clear
                print("Old commands cleared")
                
                # Copy commands to guild
                self.tree.copy_global_to(guild=test_guild)
                print("Copied new commands to test guild")
                
                # Now sync new commands
                synced = await self.tree.sync(guild=test_guild)
                print(f"  🧪 TEST {test_guild.name}: {len(synced)} command(s)")
                for cmd in synced:
                    print(f"    - {cmd.name}")
                
                if len(synced) > 0:
                    print("✅ SUCCESS! Test sync worked. Syncing to all guilds...")
                    
                    # Now sync to all guilds
                    for guild in self.guilds[1:]:  # Skip the test guild
                        try:
                            print(f"Processing guild: {guild.name}")
                            self.tree.clear_commands(guild=guild)
                            await self.tree.sync(guild=guild)  # Clear old commands
                            self.tree.copy_global_to(guild=guild)
                            synced = await self.tree.sync(guild=guild)
                            print(f"  ✅ {guild.name}: {len(synced)} command(s)")
                        except Exception as e:
                            print(f"  ❌ {guild.name}: Failed - {e}")
                            
                    # Also clear and sync global commands to remove old ones
                    print("Clearing old global commands...")
                    try:
                        self.tree.clear_commands(guild=None)  # Clear global commands
                        await self.tree.sync()  # Sync empty global tree
                        print("Old global commands cleared")
                    except Exception as e:
                        print(f"Failed to clear global commands: {e}")
                        
                else:
                    print("❌ Test sync failed - trying global clear and sync")
                    try:
                        # Clear all global commands first
                        self.tree.clear_commands(guild=None)
                        await self.tree.sync()
                        print("Cleared old global commands")
                        
                        # Add commands back and sync globally
                        for cmd in list(self.tree._global_commands.values()):
                            self.tree.add_command(cmd)
                        synced = await self.tree.sync()
                        print(f"Global sync: {len(synced)} command(s)")
                    except Exception as e:
                        print(f"Global clear and sync failed: {e}")
                        
            except Exception as e:
                print(f"Test sync failed: {e}")
                import traceback
                traceback.print_exc()
        
        print("Command sync process complete!")
        print("⚠️  If old commands still appear, try:")
        print("   1. Restart Discord client")
        print("   2. Wait 5-10 minutes for Discord cache to update")
        print("   3. Use Discord in incognito/private browsing mode")
    else:
        print("No commands found in tree - skipping sync")