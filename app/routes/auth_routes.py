from fastapi import APIRouter, Depends
from app.schemas import user_schema
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_config import get_async_db_session
from app.services.user_service import UserService
from app.utils import handle_exception


auth_router = APIRouter(prefix='/auth', tags=['Auth'])


@auth_router.post('/register', response_model=user_schema.UserDetailSchema)
@handle_exception
async def register(user_data:user_schema.RegisterSchema,
        db: Annotated[AsyncSession, Depends(get_async_db_session)]):
    
    user = await UserService.register_user(user_data, db)
    return user
    

@auth_router.post('/login')
@handle_exception
async def login(data:user_schema.LoginSchema,
    db: Annotated[AsyncSession, Depends(get_async_db_session)]):
    response = await UserService.login_user(data,db)
    print("response", response)
    return response