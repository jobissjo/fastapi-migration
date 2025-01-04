from typing import Annotated
from app.schemas import user_schema
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_config import get_async_db_session
from fastapi import Depends
from app.models.user_model import User
from sqlalchemy.future import select
from app.utils import CustomException
from app.core.auth_security import  create_access_token, hash_password, verify_password
from fastapi.security import OAuth2PasswordRequestForm

class UserService:
    
    @staticmethod
    async def register_user(user_data:user_schema.RegisterSchema,
            db: Annotated[AsyncSession, Depends(get_async_db_session)]):
        
        query = select(User).where(
            (User.username == user_data.username) |
            (User.email == user_data.email)
        )

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise CustomException("A user with this username or email already exists.",
                    400)
        user_data = user_data.model_dump().copy()
        user_data['password'] = await hash_password(user_data['password'])
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login_user(user_data:user_schema.LoginSchema,
            db: Annotated[AsyncSession, Depends(get_async_db_session)]):
        
        query = select(User).where((User.email == user_data.email))

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        if not existing_user:
            raise CustomException("email not exists",400)
        correct_pwd = await verify_password(user_data.password, existing_user.password)
        if not correct_pwd:
            raise CustomException("Invalid credentials.",401)
        access_token = await create_access_token({'user_id': existing_user.id})
        return {"access_token": access_token, "token_type": "bearer",
                'user_id': existing_user.id, 'role': existing_user.role}
    

    @staticmethod
    async def login_user_username(user_data:user_schema.LoginUsernameSchema,
            db: Annotated[AsyncSession, Depends(get_async_db_session)]):
        
        query = select(User).where((User.username == user_data.username))

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        if not existing_user:
            raise CustomException("Username with user not exists",404)
        correct_pwd = await verify_password(user_data.password, existing_user.password)
        if not correct_pwd:
            raise CustomException("Invalid credentials.",401)
        access_token = await create_access_token({'user_id': existing_user.id})
        return {"access_token": access_token, "token_type": "bearer",
                'user_id': existing_user.id, 'role': existing_user.role}
    

    @staticmethod
    async def get_user_by_id(user_id: int, db: Annotated[AsyncSession, Depends(get_async_db_session)]):
        query = select(User).where(User.id==user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise CustomException(
                f"User with id {user_id} does not exist.",
                404
            )

        return user