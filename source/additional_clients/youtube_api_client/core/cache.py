from datetime import datetime

class CacheManager:
    """
    Manages caching of YouTube API responses
    """
    def __init__(self, cache_timeout):
        """
        Initialize the cache manager
        
        Args:
            cache_timeout (timedelta): Time before cache entries expire
        """
        self.cache_timeout = cache_timeout
        self.cache_timestamp = {}  # Store timestamps for cache invalidation
        self.cache_data = {}  # Store actual cache data
    
    def get_from_cache(self, key):
        """
        Get a value from cache if it exists and is not expired
        
        Args:
            key (str): Cache key
            
        Returns:
            object: Cached value or None if not found or expired
        """
        if key in self.cache_timestamp:
            # Check if cache is expired
            if datetime.now() - self.cache_timestamp[key] < self.cache_timeout:
                return self.cache_data.get(key)
            else:
                # Expired, clean up
                self.cache_data.pop(key, None)
                self.cache_timestamp.pop(key, None)
        return None
    
    def add_to_cache(self, key, value):
        """
        Add a value to cache with current timestamp
        
        Args:
            key (str): Cache key
            value (object): Value to cache
        """
        self.cache_data[key] = value
        self.cache_timestamp[key] = datetime.now()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache_data.clear()
        self.cache_timestamp.clear()