# forms/login.py
from pydantic import BaseModel, validator

class LoginForm(BaseModel):
    username: str
    password: str
    remember_me: bool = False
    
    @validator('username')
    def username_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Имя пользователя обязательно')
        return v
    
    @validator('password')
    def password_not_empty(cls, v):
        if not v:
            raise ValueError('Пароль обязателен')
        return v