from pydantic import BaseModel, Field

from app.schemas.common_schema import UserRoleEnum

class LoginSchema(BaseModel):
    email:str
    password:str

class LoginUsernameSchema(BaseModel):
    username:str
    password:str

class RegisterSchema(LoginSchema):
    username:str
    role: UserRoleEnum = Field(default=UserRoleEnum.USER)

    class Config:
        from_properties = True

class UserDetailSchema(BaseModel):
    id:int
    email:str
    username:str
    role: UserRoleEnum

class VerifyUserSchema(BaseModel):
    email:str
    otp:str