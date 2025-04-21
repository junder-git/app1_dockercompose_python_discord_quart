"""
Base API class with core functionality for the Discord Bot API client
"""
import aiohttp
from urllib.parse import urlencode

class DiscordAPIBase:
    def __init__(self, host, port, secret_key):
        """
        Initialize the Discord Bot API base class
        
        Args:
            host (str): API host address
            port (int): API port number
            secret_key (str): Authentication secret key
        """
        self.base_url = f"http://{host}:{port}/api"
        self.secret_key = secret_key
        self.session = None
    
    async def ensure_session(self):
        """Ensure an aiohttp session exists, creating one if needed"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
    
    async def _get_request(self, endpoint, params=None, default_response=None):
        """
        Generic method for GET requests
        
        Args:
            endpoint (str): API endpoint to call
            params (dict, optional): Query parameters
            default_response (dict, optional): Default response if the request fails
            
        Returns:
            dict: Response from the API or default/error response
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            url = f"{self.base_url}/{endpoint}"
            async with self.session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return default_response or {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API ({endpoint}): {e}")
            return default_response or {"success": False, "error": str(e)}
    
    async def _post_request(self, endpoint, data):
        """
        Generic method for POST requests
        
        Args:
            endpoint (str): API endpoint to call
            data (dict): Data to send in the request body
            
        Returns:
            dict: Response from the API or error response
        """
        try:
            await self.ensure_session()
            headers = {"Authorization": f"Bearer {self.secret_key}"}
            
            url = f"{self.base_url}/{endpoint}"
            async with self.session.post(url, headers=headers, json=data) as response:
                if response.status != 200:
                    print(f"Error from bot API: {response.status}")
                    return {"success": False, "error": f"API error: {response.status}"}
                return await response.json()
        except Exception as e:
            print(f"Error calling bot API ({endpoint}): {e}")
            return {"success": False, "error": str(e)}
    
    # Public HTTP method wrappers for easier use in routes
    async def get(self, endpoint, params=None):
        """
        Public GET method wrapper for route handlers
        
        Args:
            endpoint (str): API endpoint path (can include query params)
            params (dict, optional): Additional query parameters
            
        Returns:
            Response: aiohttp ClientResponse object
        """
        await self.ensure_session()
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        
        # If endpoint already has query params, preserve them
        if '?' in endpoint and params:
            query_string = urlencode(params)
            url = f"{self.base_url}{endpoint}&{query_string}"
        elif params:
            query_string = urlencode(params)
            url = f"{self.base_url}{endpoint}?{query_string}"
        else:
            url = f"{self.base_url}{endpoint}"
            
        return await self.session.get(url, headers=headers)
    
    async def post(self, endpoint, data=None):
        """
        Public POST method wrapper for route handlers
        
        Args:
            endpoint (str): API endpoint path
            data (dict, optional): JSON data to send
            
        Returns:
            Response: aiohttp ClientResponse object
        """
        await self.ensure_session()
        headers = {"Authorization": f"Bearer {self.secret_key}"}
        url = f"{self.base_url}{endpoint}"
        return await self.session.post(url, headers=headers, json=data)
    
    async def close(self):
        """Close the session when done"""
        if self.session:
            await self.session.close()
            self.session = None