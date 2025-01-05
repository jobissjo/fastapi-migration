from fastapi import HTTPException, status
from functools import wraps
from typing import Callable
from app.core.logger_config import logger

class CustomException(Exception):
    def __init__(self, message: str, status_code:int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)

def handle_exception(route_handler:Callable):
    @wraps(route_handler)
    async def wrapper(*args, **kwargs):
        try:
            logger.info("Request handling started")
            return await route_handler(*args, **kwargs)
        except CustomException as e:
            logger.error(f"Exception: {e.message} with status code {e.status_code}")
            raise HTTPException(status_code=e.status_code, 
                detail=e.message)
        except Exception as e:
            logger.error(f"Unexpected error occurred: {str(e)}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"An unexpected error occurred: {e}")
    
    return wrapper