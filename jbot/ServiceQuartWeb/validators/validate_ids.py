"""
ID validation functions
"""
import re
import secrets

def validate_guild_id(guild_id):
    """
    Validate Discord guild ID
    
    Args:
        guild_id (str): Guild ID to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not guild_id:
        return False
    
    # Check if guild_id is a valid numeric string
    return bool(re.match(r'^\d+$', str(guild_id)))

def validate_channel_id(channel_id, available_channels=None):
    """
    Validate channel ID against available channels
    
    Args:
        channel_id (str): Channel ID to validate
        available_channels (list, optional): List of available channels
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not channel_id:
        return False
    
    # Check if channel_id is a valid numeric string
    if not re.match(r'^\d+$', str(channel_id)):
        return False
    
    # If no available channels provided, assume the ID is valid
    if available_channels is None:
        return True
    
    # Check if channel exists in available channels
    return any(str(channel.get('id')) == str(channel_id) for channel in available_channels)

def generate_csrf_token():
    """
    Generate a secure CSRF token
    
    Returns:
        str: CSRF token
    """
    return secrets.token_hex(32)