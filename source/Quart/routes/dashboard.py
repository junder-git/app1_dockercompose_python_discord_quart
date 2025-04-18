"""
Dashboard route for JBot Quart application
"""
from quart import Blueprint, render_template, redirect, url_for, session
from .helpers import login_required
import traceback

# Create a blueprint for dashboard route
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route("/dashboard")
@login_required
async def dashboard_route():
    """Main dashboard page listing servers"""
    try:
        # Import from current app context to avoid circular imports
        from quart import current_app
        discord = current_app.discord
        bot_api = current_app.bot_api
        
        # First, verify we have the necessary session data
        if 'user_id' not in session:
            print("No user_id in session, redirecting to login")
            return redirect(url_for("login.login_route"))
            
        # Get guild information
        guild_count = 0
        guild_ids = []
        try:
            guild_count = await bot_api.get_guild_count()
            guild_ids = await bot_api.get_guild_ids()
            print(f"Bot guild count: {guild_count}")
            print(f"Bot guild IDs: {guild_ids}")
        except Exception as e:
            print(f"Error getting bot guild info: {e}")
            # Continue anyway, showing guilds without bot presence
        
        # Fetch user
        user = await discord.fetch_user()
        
        # Fetch user guilds
        user_guilds = await discord.fetch_guilds()
        print(f"User has {len(user_guilds)} guilds")
        
        # Print user guild IDs for debugging
        user_guild_ids = [str(g.id) for g in user_guilds]  # Convert to strings
        print(f"User guild IDs: {user_guild_ids}")
        
        # Type-safe comparison of guild IDs
        same_guilds = []
        for guild in user_guilds:
            guild_id_str = str(guild.id)
            print(f"Checking guild: {guild.name} (ID: {guild_id_str})")
            
            if guild_id_str in guild_ids:
                print(f"Match found! Guild: {guild.name}")
                same_guilds.append(guild)
        
        print(f"Found {len(same_guilds)} mutual guilds out of {len(user_guilds)} total user guilds")
        print(f"Same guilds: {[g.name for g in same_guilds]}")
        
        has_no_mutual_guilds = len(same_guilds) == 0
        print(f"has_no_mutual_guilds = {has_no_mutual_guilds}")
                
        # Pass config for bot invite link
        config = {
            "DISCORD_CLIENT_ID": current_app.config["DISCORD_CLIENT_ID"]
        }
        
        return await render_template(
            "dashboard.html", 
            guild_count=guild_count, 
            matching=same_guilds, 
            user=user, 
            guilds=same_guilds,  # Using same_guilds for both matching and guilds
            has_no_mutual_guilds=has_no_mutual_guilds,
            bot_check_errors=False,
            config=config
        )
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Log the full traceback for better debugging
        traceback.print_exc()
        # Clear session and redirect to login on error
        session.clear()
        return redirect(url_for("login.login_route"))