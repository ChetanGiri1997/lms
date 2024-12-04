from pydantic import BaseModel, Field, constr, EmailStr
from typing import Optional, Annotated
from .common import PyObjectId
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: EmailStr  # Add email field
    first_name: str  # Add first name field
    last_name: str  # Add last name field
    role: str

class UserCreate(UserBase):
    password: str

class UserInDB(BaseModel):
    id: Optional[str]
    username: str
    password: str
    email: EmailStr
    first_name: str
    last_name: str
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True
    profile_picture: Optional[str] = None  # Add profile picture path

    class Config:
        from_attributes = True


class User(UserBase):
    id: str = Field(default_factory=str, alias="_id")
    profile_picture: Optional[str] = None

    class Config:
        json_encoders = {PyObjectId: str}
        populate_by_name = True

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    first_name: str
    last_name: str
    role: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    id: str
    profile_picture: Optional[str] = None

class TokenData(BaseModel):
    username: str
    role: str
    # profile_picture: Optional[str] = None

class LoginRequest(BaseModel):
    username_or_email: str  # Update to accept either username or email
    password: str

class UserUpdate(BaseModel):
    username: Optional[Annotated[str, constr(min_length=3, max_length=30)]] = None
    email: Optional[EmailStr] = None  # Add email for update
    first_name: Optional[str] = None  # Add first name for update
    last_name: Optional[str] = None  # Add last name for update
    role: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "username": "new_username",
                "email": "new_email@example.com",
                "first_name": "NewFirstName",
                "last_name": "NewLastName",
                "password": "new_password",
                "role": "role"
            }
        }

class UserRegister(BaseModel):
    username: str
    email: EmailStr  # Email is required for registration
    first_name: str
    last_name: str
    password: str
    role: Optional[str] = 'student'  # Default role can be 'user'
    profile_picture: Optional[str] = None

class UserLogin(BaseModel):
    identifier: str  # This can be username or email
    password: str

class SwaggerToken(BaseModel):
    username: str
    password: str

class UserProfileOut(BaseModel):
    id: str
    username: str
    email: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    role: str = Field(default="student")
    is_active: Optional[bool]
    profile_picture: Optional[str]