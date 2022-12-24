from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Login(BaseModel):
    username_or_email: str
    password: str

class ModifyUser(BaseModel):
    email: str
    username: str
    password: str

class ResetKey(BaseModel):
    reset_key: str

class ResetPasswordCreds(BaseModel):
    email: str
    

class UserResponse(BaseModel):
    id: int
    biography: Optional[str]
    birthdate: Optional[str]
    company: Optional[str]
    created_at: datetime
    display_birthday: bool
    email: Optional[str]
    fullname: Optional[str]
    location: Optional[str]
    username: str
    website: Optional[str]

class MeResponse(BaseModel):
    id: int
    biography: Optional[str]
    birthdate: Optional[str]
    company: Optional[str]
    created_at: datetime
    display_birthday: bool
    email: str
    email_public: bool
    fullname: Optional[str]
    hide_inappropriate: bool
    location: Optional[str]
    username: str
    website: Optional[str]

class ModifyItem(BaseModel):
    name: str
    description: str
    instructions: str
    license: str
    version: str

class ModifyProfile(BaseModel):
    fullname: str
    location: str
    company: str
    biography: str

class RevisionUpload(BaseModel):
    item_revision_id: int
