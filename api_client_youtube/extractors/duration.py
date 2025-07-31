import re

def parse_duration(duration_str):
    """
    Parse ISO 8601 duration to seconds
    e.g. PT1H30M15S -> 5415 seconds
    
    Args:
        duration_str (str): ISO 8601 duration string
        
    Returns:
        int: Duration in seconds
    """
    if not duration_str:
        return 0
        
    hours = 0
    minutes = 0
    seconds = 0
    
    # Extract hours
    hour_match = re.search(r'(\d+)H', duration_str)
    if hour_match:
        hours = int(hour_match.group(1))
    
    # Extract minutes
    minute_match = re.search(r'(\d+)M', duration_str)
    if minute_match:
        minutes = int(minute_match.group(1))
    
    # Extract seconds
    second_match = re.search(r'(\d+)S', duration_str)
    if second_match:
        seconds = int(second_match.group(1))
    
    return hours * 3600 + minutes * 60 + seconds

def format_duration(seconds):
    """
    Format duration in seconds to a readable string (MM:SS or HH:MM:SS)
    
    Args:
        seconds (int): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds is None or seconds <= 0:
        return "00:00"
    
    # Ensure we're working with an integer
    seconds = int(seconds)
        
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"