from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas import user_schema
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_config import get_async_db_session
from app.services.user_service import UserService
from app.utils import handle_exception
from app.models.user_model import User
from app.core.auth_security import verify_token_get_user
import redis.asyncio as redis
from app.core.redis_config import get_redis_client



auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post('/register')
@handle_exception
async def register(user_data:user_schema.RegisterSchema,
        db: Annotated[AsyncSession, Depends(get_async_db_session)],
        redis: redis.Redis = Depends(get_redis_client)):
    
    user = await UserService.register_user(user_data, db)
    
    return await UserService.send_otp(user.email, redis)

@auth_router.post('/verify_user')
@handle_exception
async def verify_user(body:user_schema.VerifyUserSchema,
            db: Annotated[AsyncSession, Depends(get_async_db_session)],
            redis:redis.Redis = Depends(get_redis_client)):
    return await UserService.verify_user(body, db, redis)

@auth_router.post('/login')
@handle_exception
async def login(data:user_schema.LoginSchema,
    db: Annotated[AsyncSession, Depends(get_async_db_session)]):
    response = await UserService.login_user(data,db)
    return response


@auth_router.post('/token')
@handle_exception
async def login_with_username(db: Annotated[AsyncSession, Depends(get_async_db_session)],
        data:OAuth2PasswordRequestForm=Depends()):
    new_data = user_schema.LoginUsernameSchema(username=data.username, password=data.password)
    response = await UserService.login_user_username(new_data,db)
    return response


@auth_router.get('/user-profile', response_model=user_schema.UserDetailSchema)
@handle_exception
async def user_profile(current_user: User = Depends(verify_token_get_user),):
    return current_user