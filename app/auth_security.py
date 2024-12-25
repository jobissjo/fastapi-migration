from datetime import datetime, timedelta, timezone
from jose import jwt
from app import config
from app.utils import CustomException
import bcrypt
import asyncio
from typing import Optional

async def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    # Prepare the payload data and expiration time
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(hours=1))  # Use UTC with timezone
    to_encode.update({"exp": expire})
    
    # Offload the blocking jwt.encode function to a separate thread using asyncio.to_thread
    return await asyncio.to_thread(jwt.encode, to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)


async def verify_token(token: str):
    try:
        payload = jwt.decode(token, config.SECRET_KEY,
                algorithms=[config.ALGORITHM])
        return payload
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