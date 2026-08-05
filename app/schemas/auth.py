# app/schemas/auth.py
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator

PASSWORD_SPECIAL_CHARS = r"!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>/?"


class SignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=64)
    nickname: str = Field(min_length=2, max_length=50)

    @field_validator("password")
    @classmethod
    def password_complexity(cls, v: str) -> str:
        if not any(c.isupper() for c in v):
            raise ValueError("비밀번호는 대문자를 1개 이상 포함해야 합니다.")
        if not any(c.islower() for c in v):
            raise ValueError("비밀번호는 소문자를 1개 이상 포함해야 합니다.")
        if not any(c.isdigit() for c in v):
            raise ValueError("비밀번호는 숫자를 1개 이상 포함해야 합니다.")
        if not any(c in PASSWORD_SPECIAL_CHARS for c in v):
            raise ValueError("비밀번호는 특수문자를 1개 이상 포함해야 합니다.")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    nickname: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
