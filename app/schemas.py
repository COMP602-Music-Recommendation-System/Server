from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
# In schemas.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str


# Pydantic models for JWT token data
class TokenData(BaseModel):
    username: str

# User Create and Response
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# User Preferences Schema
class UserPreferencesResponse(BaseModel):
    id: int
    user_id: int
    genre_preference: Optional[List[str]]
    artist_preference: Optional[List[str]]
    language_preference: Optional[List[str]]

    class Config:
        from_attributes = True
