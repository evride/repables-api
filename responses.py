from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from typing import List

class BaseUserResponse(BaseModel):
    id: int
    username: str

class UserResponse(BaseUserResponse):
    biography: Optional[str]
    birthdate: Optional[date]
    company: Optional[str]
    created_at: datetime
    email: Optional[str]
    fullname: Optional[str]
    location: Optional[str]
    website: Optional[str]

class MeResponse(UserResponse):
    display_birthday: bool
    email_public: bool
    hide_inappropriate: bool

class Image(BaseModel):
    url: str
    width: int
    height: int

class ImageSizes(BaseModel):
    small: Image
    large: Image

class ItemResponse(BaseModel):
    id: int
    revision_id: int
    name: str
    description: str
    instructions: str
    tags: Optional[str]
    license: str
    version: str
    flagged_at: Optional[datetime]
    previewImage: Optional[ImageSizes]
    images: Optional[List[ImageSizes]]
    user: Optional[BaseUserResponse]

class PaginatedItemsResponse(BaseModel):
    offset: int
    limit: int
    count: Optional[int]
    results: List[ItemResponse]
class PaginatedSearchResponse(PaginatedItemsResponse):
    q: str

class PaginatedUsersResponse(BaseModel):
    offset: int
    limit: int
    count: Optional[int]
    results: List[UserResponse]
