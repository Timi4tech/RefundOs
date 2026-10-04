from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        value = " ".join(v.split())
        if not value: raise ValueError("Name is required.")
        return value
class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    name: str
    role: str
class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
