from typing import Optional, Dict
from anthropic.types import APIError
import logging
import asyncio

class APIErrorHandler:
    """Handles Anthropic API errors with retry logic"""
    
    ERROR_MESSAGES = {
        "rate_limit_error": "Rate limit exceeded. Waiting before retry...",
        "invalid_request_error": "Invalid request parameters",
        "authentication_error": "API key authentication failed",
        "permission_error": "Insufficient permissions for this operation",
        "not_found_error": "Requested resource not found",
        "server_error": "Anthropic API server error"
    }
    
    @staticmethod
    async def handle_error(error: APIError) -> Optional[Dict]:
        """Handle different types of API errors"""
        error_type = error.type
        
        if error_type == "rate_limit_error":
            # Implement exponential backoff
            await asyncio.sleep(error.retry_after or 1)
            return {"should_retry": True, "wait_time": error.retry_after}
            
        elif error_type == "server_error":
            # Log server errors
            logging.error(f"Anthropic API server error: {error.message}")
            return {"should_retry": True, "wait_time": 5}
            
        else:
            # Log other errors
            logging.error(f"API error: {error.type} - {error.message}")
            return {"should_retry": False, "error": error.message} 