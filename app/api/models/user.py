from pydantic import BaseModel, EmailStr, Field


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Plain password"
    )


class UserCreateResponse(BaseModel):
    message: str = "User created. Activation code sent."
