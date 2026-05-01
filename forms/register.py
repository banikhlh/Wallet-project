# forms/register.py
from pydantic import BaseModel, validator, EmailStr
from typing import Optional

class RegistrationForm(BaseModel):
    username: str
    email: EmailStr
    password: str
    confirm_password: str
    agree_terms: bool = False
    
    @validator('username')
    def username_length(cls, v):
        if len(v) < 3:
            raise ValueError('Имя пользователя должно содержать минимум 3 символа')
        if len(v) > 50:
            raise ValueError('Имя пользователя не должно превышать 50 символов')
        return v
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 6:
            raise ValueError('Пароль должен содержать минимум 6 символов')
        if not any(char.isdigit() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну цифру')
        if not any(char.isupper() for char in v):
            raise ValueError('Пароль должен содержать хотя бы одну заглавную букву')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v
    
    @validator('agree_terms')
    def terms_accepted(cls, v):
        if not v:
            raise ValueError('Вы должны согласиться с условиями')
        return v