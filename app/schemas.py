from datetime import datetime
from pydantic import BaseModel,ConfigDict

class UserCreate(BaseModel):
    email:str
    password:str
    level:str="A0"


class UserResponse(BaseModel):
    id:int
    email:str
    name:str | None
    level:str
    created_at:datetime
    model_config=ConfigDict(from_attributes=True)



class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class GoogleLogin(BaseModel):
    id_token: str


class AppleLogin(BaseModel):
    identity_token: str
    nonce: str
    email: str | None = None
    name: str | None = None

class ProfileUpdate(BaseModel):
    name:str | None =None
    level:str | None =None




class FavoriteWordCreate(BaseModel):
    word: str
    translation: str
    example_1: str | None = None
    example_2: str | None = None
    example_translation_1: str | None = None
    example_translation_2: str | None = None
    level: str | None = None


class FavoriteWordResponse(BaseModel):
    id: int
    word: str
    translation: str
    example_1: str | None
    example_2: str | None
    example_translation_1: str | None
    example_translation_2: str | None
    level: str | None
    favorited_at: datetime

    model_config = ConfigDict(from_attributes=True)