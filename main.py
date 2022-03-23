from typing import Optional

from fastapi import FastAPI, UploadFile, Depends
import peewee
import aiofiles
import time

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

class ModifyItem(BaseModel):
    name: str
    description: str
    instructions: str
    license: str
    version: str

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    item = model_to_dict(Item.select().where(Item.id == item_id).get())
    return {"item_id": item_id, "q": q}

@app.get("/items/")
def read_items():
    items = Item.select()
    items = [model_to_dict(item) for item in items]
    return items


@app.get("/users/")
def read_users():
    users = User.select()
    users = [model_to_dict(user) for user in users]
    return users

@app.post("/user")
def create_user(user: ModifyUser):
    try:
        u = User.create(email = user.email, username = user.username, password = get_password_hash(user.password))
    except:
        return { "error" : "User already exist"}
    return model_to_dict(u)

@app.get("/me")
def read_user(current_user: User = Depends(get_current_user)):
    return model_to_dict(current_user)

@app.post("/item")
def create_item(item: ModifyItem, current_user: User = Depends(get_current_user)):
    i = ItemRevision.create(**dict(item), user_id=current_user.id)
    return model_to_dict(i)

@app.post("/file")
async def create_file(file: UploadFile, current_user: User = Depends(get_current_user)):
    file_location = "uploaded_files/" + str(time.time())
    try:
        async with aiofiles.open(file_location, 'wb') as out_file:
            content = await file.read()  # async read
            size = len(content)
            await out_file.write(content)  # async write
            item_upload = ItemUpload(uploader=current_user.id, filename = file.filename, file_location = file_location, size = size, mimetype = file.content_type)
            item_upload.save()
    except Exception as e:
        print(e)
    return model_to_dict(item_upload)

@app.put("/user/{user_id}")
def edit_user(user_id : int, user: ModifyUser):
    u = User.update(user.dict()).where(User.id == user_id).execute()
    updated_u = model_to_dict(User.select().where(User.id == user_id).get())
    return updated_u

@app.delete("/user/{user_id}")
def delete_user(user_id : int):
    u = User.get(User.id == user_id)
    return u.delete_instance()

@app.post('/login')
async def login_user(creds: Login):
    u = User.select().where(User.username == creds.username_or_email).get()
    user = model_to_dict(u)
    if not user:
        return { 'error': 'Username or email does not exist.' }
    if not verify_password(creds.password, user['password']):
        return False
    if user['id'] >= 1:
        token_data = {'id': user['id']}
        return {'token': create_access_token(token_data)}
    else:
        return {"error": "Username or password is incorrect"}
