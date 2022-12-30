from fastapi import APIRouter
import subprocess

from fastapi import FastAPI, UploadFile, Depends, File, Form, Request
import peewee
import aiofiles
import time
from datetime import datetime

from playhouse.shortcuts import *
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from models import Item, User, Item, ItemRevision, ItemUpload, PasswordReset, ItemView
from utils import create_access_token, get_password_hash, verify_password, require_current_user, get_current_user, reset_password_key
from requests import Login, ModifyUser, ResetKey, ResetPasswordCreds, ModifyItem, ModifyProfile, RevisionUpload
from responses import UserResponse, MeResponse


router = APIRouter()


@router.get("/users/{username}", tags=["users"])
async def read_user(username: str):
    return {"username": username}
    
@router.get('/user/{user_id}', response_model = UserResponse, tags=["users"])
async def read_user(user_id: int):
    u = User.select().where(User.id == user_id).get()
    if(u.email_public == False):
        u.email = None
    return model_to_dict(u)

@router.get("/users/", tags=["users"])
async def read_users():
    users = User.select()
    users = [model_to_dict(user) for user in users]
    return users

@router.post("/user", tags=["users"])
async def create_user(user: ModifyUser):
    try:
        u = User.create(email = user.email, username = user.username, password = get_password_hash(user.password))
    except:
        return { "error" : "User already exist"}
    return model_to_dict(u)

@router.put("/user", tags=["users"])
async def update_user(user: ModifyProfile, current_user: User = Depends(require_current_user)):
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

@router.get("/me", response_model = MeResponse, tags=["users"])
async def read_current_user(current_user: User = Depends(require_current_user)):
    return model_to_dict(current_user)
    
@router.put("/user/{user_id}", tags=["users"])
async def edit_user(user_id : int, user: ModifyUser):
    u = User.update(user.dict()).where(User.id == user_id).execute()
    updated_u = model_to_dict(User.select().where(User.id == user_id).get())
    return updated_u

@router.delete("/user/{user_id}", tags=["users"])
async def delete_user(user_id : int):
    u = User.get(User.id == user_id)
    return u.delete_instance()

@router.post('/login', tags=["users"])
async def login_user(creds: Login):
    print(creds)
    u = User.select().where(User.username == creds.username_or_email).get()
    user = model_to_dict(u)
    if not user:
        return { 'error': 'Username or email does not exist.' }
    if not await verify_password(creds.password, user['password']):
        return { 'error': 'Password is incorrect.' }
    if user['id'] >= 1:
        token_data = {'id': user['id']}
        token = await create_access_token(token_data);

        return {'token': token, 'id': user['id'], 'username': user['username']}
    else:
        return {'error': 'Username or password is incorrect.'}

@router.post('/reset-password', tags=["users"])
async def create_reset_password_key(creds: ResetPasswordCreds):
    u = User.select().where(User.email == creds.email).get()

    if (u):
        key = PasswordReset.create(user_id = u.id, reset_key = reset_password_key)
        key.save()
        #logic for emailing the key to the user goes here
        return {'status' :'success'}
    else:
        return {'error': 'Email not found.'}

