from typing import Annotated
from app.schemas import user_schema
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db_config import get_async_db_session
from fastapi import Depends
from app.models.user_model import User
from sqlalchemy.future import select
from app.utils import CustomException, generate_otp, render_email_template, send_email
from app.core.auth_security import  create_access_token, hash_password, verify_password
from app.services.redis_service import RedisService
import redis.asyncio as redis

class UserService:
    
    @staticmethod
    async def register_user(user_data:user_schema.RegisterSchema,
            db: AsyncSession):
        
        query = select(User).where(
            (User.username == user_data.username) |
            (User.email == user_data.email)
        )

        result = await db.execute(query)
        existing_user = result.scalar_one_or_none()
        if existing_user and existing_user.is_active:
            raise CustomException("A user with this username or email already exists.",
                    400)
        
        user_data = user_data.model_dump().copy()
        hashed_password = await hash_password(user_data['password'])
        if not existing_user: 
            user_data['password'] = hashed_password
            user = User(**user_data)
            db.add(user)
            await db.commit()
            await db.refresh(user)
            return user
        elif not existing_user.is_active and  existing_user.email == user_data['email']:
            existing_user.password = hashed_password
            existing_user.username = user_data['username']
            existing_user.role = user_data['role']
            await db.commit()
            await db.refresh(existing_user)
            return existing_user
        else:
            raise CustomException("A user with this username already exists.",
                    400)
        
    @staticmethod
    async def login_user(user_data:user_schema.LoginSchema,
            db: AsyncSession):
        
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
            db: AsyncSession):
        
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
    async def get_user_by_id(user_id: int, db: AsyncSession):
        query = select(User).where(User.id==user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise CustomException(
                f"User with id {user_id} does not exist.",
                404
            )

        return user
    
    @staticmethod
    async def __get_user_by_email(email: str, db: AsyncSession):
        query = select(User).where(User.email==email)
        result = await db.execute(query)
        user = result.scalar_one_or_none()
        if user is None:
            raise CustomException(
                f"User with email '{email}' does not exist.",
                404
            )

        return user
    
    @staticmethod
    async def verify_user(verify_data:user_schema.VerifyUserSchema,
            db: AsyncSession,
            redis:redis.Redis):
        user = await UserService.__get_user_by_email(email=verify_data.email, db=db)
        is_correct = await RedisService.verify_otp(**verify_data.model_dump(), redis=redis)
        if not is_correct:
            raise CustomException(message="Invalid otp", status_code=400)
        
        user.is_active = True
        await db.commit()
        await db.refresh(user)

        return {'message': 'Verified otp successfully'}
    
    @staticmethod
    async def send_otp(email:str, redis_client: redis.Redis):
        otp = await generate_otp()
        await RedisService.set_otp(email, otp, redis=redis_client)

        # Send a otp in email
        body = await render_email_template('verify_account.html', 
                        email=email, otp=otp)
        await send_email(email, 'Verify Your Account', body)

        return {'message': "Otp send to registered email successfully"}