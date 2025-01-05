
import redis.asyncio as redis
from app.core.config import EXPIRE_OTP_SECONDS
from app.utils import CustomException

class RedisService:
    @staticmethod
    async def set_otp(email:str , otp: str, redis: redis.Redis):
        await redis.setex(f"otp_{email}", EXPIRE_OTP_SECONDS, otp)
    
    @staticmethod
    async def verify_otp(email:str, otp:str, redis:redis.Redis):
        
        stored_otp = await redis.get(f"otp_{email}")
        if not stored_otp:
            raise CustomException(message="No otp available", status_code=400)
        print(str(stored_otp.decode('utf-8')), otp, email)

        return str(stored_otp.decode('utf-8')) == otp
            
        
        
    
        

