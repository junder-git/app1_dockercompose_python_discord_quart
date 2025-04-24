"""
Logging utilities for Discord Bot
"""
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Configure logging
def setup_logging(name='jbot', level=logging.INFO):
    """
    Set up logging configuration
    
    Args:
        name: Logger name
        level: Logging level
        
    Returns:
        logging.Logger: Configured logger
    """
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create file handler
    log_filename = f"logs/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename)
    file_handler.setFormatter(formatter)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Configure logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_logger(name='jbot'):
    """
    Get or create a logger
    
    Args:
        name: Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    logger = logging.getLogger(name)
    
    # If logger isn't configured yet, set it up
    if not logger.handlers:
        return setup_logging(name)
    
    return logger

# Log formatting functions
def log_command(logger, ctx, command_name):
    """
    Log a command execution
    
    Args:
        logger: Logger instance
        ctx: Discord command context
        command_name: Name of the command
    """
    logger.info(
        f"Command '{command_name}' executed by {ctx.author} (ID: {ctx.author.id}) "
        f"in guild {ctx.guild.name} (ID: {ctx.guild.id}), "
        f"channel: {ctx.channel.name} (ID: {ctx.channel.id})"
    )

def log_api_request(logger, request, handler_name):
    """
    Log an API request
    
    Args:
        logger: Logger instance
        request: aiohttp request object
        handler_name: Name of the handler function
    """
    logger.info(
        f"API request to {handler_name} from {request.remote} "
        f"with method {request.method} and path {request.path}"
    )

def log_error(logger, error, context=None):
    """
    Log an error
    
    Args:
        logger: Logger instance
        error: Exception or error message
        context: Optional context information
    """
    if context:
        logger.error(f"Error in {context}: {error}", exc_info=True)
    else:
        logger.error(f"Error: {error}", exc_info=True)