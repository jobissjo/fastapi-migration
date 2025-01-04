from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core import config
from app.utils import CustomException
import bcrypt
import asyncio
from typing import Optional, Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from app.core.db_config import get_async_db_session
from sqlalchemy.ext.asyncio import AsyncSession




oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Prepare the payload data and expiration time
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))  # Use UTC with timezone
    to_encode.update({"exp": expire})
    
    # Offload the blocking jwt.encode function to a separate thread using asyncio.to_thread
    return await asyncio.to_thread(jwt.encode, to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


async def verify_token_get_user(db: Annotated[AsyncSession, Depends(get_async_db_session)],token: str = Depends(oauth2_scheme),
                                 ):
    try:
        payload = jwt.decode(token, config.SECRET_KEY,
                algorithms=[config.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise CustomException("Token is missing user id", status_code=401)
        from app.services.user_service import UserService
        return await UserService.get_user_by_id(user_id, db)
        
        
    except jwt.ExpiredSignatureError:
        raise CustomException("Token has expired", status_code=401)
    except jwt.JWTError as e:
        raise ValueError(f"Token is invalid: {e}", status_code=401)
    
    

async def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

async def verify_password(input_password:str, stored_password:str)-> bool:
    return bcrypt.checkpw(input_password.encode('utf-8'), stored_password.encode('utf-8'))