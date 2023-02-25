from pydantic import BaseModel, Field
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

class LikePost(BaseModel):
    score: int

class ResetPasswordCreds(BaseModel):
    email: str

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

class PageRequest(BaseModel):
    limit: Optional[int] = Field(20, gt=0, le=100)
    offset: Optional[int] = Field(0, gt=0)