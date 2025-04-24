# validate_search.py
async def validate_search_params(request_data):
    """Validate search parameters from a request"""
    errors = []
    if not request_data.get('query'):
        errors.append("Search query is required")
    if not request_data.get('channel_id'):
        errors.append("Channel ID is required")
    return errors