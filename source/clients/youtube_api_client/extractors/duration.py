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