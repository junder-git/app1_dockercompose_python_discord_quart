def get_ffmpeg_options(quality='medium'):
    """
    Get FFmpeg options for audio playback
    
    Args:
        quality (str): Audio quality level (low, medium, high)
        
    Returns:
        dict: FFmpeg options
    """
    base_options = {
        'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    }
    
    if quality == 'low':
        base_options['options'] = '-vn -af "loudnorm=I=-16:TP=-1.5:LRA=11, aresample=48000, asetrate=48000*0.9"'
    elif quality == 'high':
        base_options['options'] = '-vn -af "loudnorm=I=-14:TP=-1:LRA=9" -b:a 192k'
    else:  # medium (default)
        base_options['options'] = '-vn -af "loudnorm=I=-16:TP=-1.5:LRA=11"'
        
    return base_options