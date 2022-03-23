from typing import Optional

from fastapi import FastAPI, UploadFile, Depends, File, Form
import peewee
import aiofiles
import time
from datetime import datetime
from PIL import Image

from playhouse.shortcuts import *
from config import DATABASE
from models import User, Item, ItemRevision, ItemUpload
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from utils import create_access_token, get_password_hash, verify_password, get_current_user
app = FastAPI()



origins = [
    "https://api.repables.com",
    "https://dev.repables.com",
    "http://dev.repables.com:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Login(BaseModel):
    username_or_email: str
    password: str

class ModifyUser(BaseModel):
    email: str
    username: str
    password: str

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

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    item = model_to_dict(Item.select().where(Item.id == item_id).get())
    return item

@app.get("/items/")
async def read_items():
    items = Item.select()
    items = [model_to_dict(item) for item in items]
    return items

@app.post("/item")
async def create_item(current_user: User = Depends(get_current_user)):
    i = ItemRevision.create( user_id=current_user.id)
    return model_to_dict(i)

@app.post("/item/{item_revision_id}")
async def update_item(item_revision_id : int, item: ModifyItem, current_user: User = Depends(get_current_user)):
    i = ItemRevision.select().where(ItemRevision.id == item_revision_id).where(ItemRevision.user_id == current_user.id).get()
    if(i):
        i.name = item.name
        i.description = item.description
        i.license = item.license
        i.version = item.version
        i.instructions = item.instructions
        i.save()
        return model_to_dict(i)
    else:
        return {'error' : 'Not Found'}

@app.get('/user/{user_id}', response_model = UserResponse)
async def read_user(user_id: int):
    u = User.select().where(User.id == user_id).get()
    if(u.email_public == False):
        u.email = None
    return model_to_dict(u)

@app.get("/users/")
async def read_users():
    users = User.select()
    users = [model_to_dict(user) for user in users]
    return users

@app.post("/user")
async def create_user(user: ModifyUser):
    try:
        u = User.create(email = user.email, username = user.username, password = get_password_hash(user.password))
    except:
        return { "error" : "User already exist"}
    return model_to_dict(u)

@app.put("/user")
async def update_user(user: ModifyProfile, current_user: User = Depends(get_current_user)):
    u = User.select().where(User.id == current_user.id).get()
    if(u):
        u.fullname = user.fullname
        u.location = user.location
        u.company = user.company
        u.biography = user.biography
        u.save()
        return model_to_dict(u)
    else:
        return {'error' : 'Not Found'}

@app.get("/me", response_model = MeResponse)
async def read_current_user(current_user: User = Depends(get_current_user)):
    return model_to_dict(current_user)

@app.post("/file/{revision_id}")
async def create_file(revision_id : str, file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    file_location = "uploaded_files/" + str(time.time())
    print(file)
    try:
        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await file.read()  # async read
            size = len(content)
            await out_file.write(content)  # async write
            file_name_split = file.filename.split('.')
            file_extension = ''
            if (len(file_name_split) >= 2):
                file_extension = file_name_split[-1]
            if (file.content_type == 'image/png'):
                with Image.open(file_location) as im:
                    im.thumbnail((128, 128))
                    im.save(file_location + '_thumbnail.png', 'PNG')
            item_upload = ItemUpload(uploader=current_user.id, revision_id = revision_id, filename = file.filename, file_location = file_location, size = size, mimetype = file.content_type, file_extension = file_extension )
            item_upload.save()
    except Exception as e:
        print(e)
    return model_to_dict(item_upload)

@app.put("/user/{user_id}")
async def edit_user(user_id : int, user: ModifyUser):
    u = User.update(user.dict()).where(User.id == user_id).execute()
    updated_u = model_to_dict(User.select().where(User.id == user_id).get())
    return updated_u

@app.delete("/user/{user_id}")
async def delete_user(user_id : int):
    u = User.get(User.id == user_id)
    return u.delete_instance()

@app.post('/login')
async def login_user(creds: Login):
    u = User.select().where(User.username == creds.username_or_email).get()
    user = model_to_dict(u)
    if not user:
        return { 'error': 'Username or email does not exist.' }
    if not await verify_password(creds.password, user['password']):
        return False
    if user['id'] >= 1:
        token_data = {'id': user['id']}
        token = await create_access_token(token_data);

        return {'token': token, 'id': user['id'], 'username': user['username']}
    else:
        return {"error": "Username or password is incorrect"}
