from typing import Annotated
from app.schemas import user_schema
from sqlalchemy.ext.asyncio import AsyncSession
from app.db_config import get_async_db_session
from fastapi import Depends
from app.models import user_model
from sqlalchemy.future import select
from app.utils import CustomException
from app.auth_security import  create_access_token, hash_password, verify_password


class UserService:
    
    @staticmethod
    async def register_user(user_data:user_schema.RegisterSchema,
            db: Annotated[AsyncSession, Depends(get_async_db_session)]):
        
        query = select(user_model.User).where(
            (user_model.User.username == user_data.username) |
            (user_model.User.email == user_data.email)
        )

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise CustomException("A user with this username or email already exists.",
                    400)
        user_data = user_data.model_dump().copy()
        user_data['password'] = hash_password(user_data['password'])
        user = user_model.User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def login_user(user_data:user_schema.LoginSchema,
            db: Annotated[AsyncSession, Depends(get_async_db_session)]):
        
        query = select(user_model.User).where((user_model.User.email == user_data.email))

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        if not existing_user:
            raise CustomException("email not exists",400)
        correct_pwd = await verify_password(user_data.password, existing_user.password)
        if not correct_pwd:
            raise CustomException("Invalid credentials.",401)
        access_token = await create_access_token({'user_id': existing_user.id, 'role': existing_user.role})
        return {"access_token": access_token, "token_type": "bearer"}