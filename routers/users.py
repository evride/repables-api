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
from  tortoise.expressions import Q

#from models import Item, User, Item, ItemRevision, ItemUpload, PasswordReset, ItemView
from models_tortoise import Item, User, ItemRevision, ItemUpload, PasswordReset, ItemView
from auth import create_access_token, get_password_hash, verify_password, require_current_user, reset_password_key, is_legacy_password
from requests import Login, ModifyUser, ResetKey, ResetPasswordCreds, ModifyItem, ModifyProfile, RevisionUpload
from responses import UserResponse, MeResponse


router = APIRouter()
    
@router.get('/user/{user_id}', response_model = UserResponse, tags=["users"])
async def read_user(user_id: int):
    u = await User.get(id = user_id)
    if(u.email_public == False):
        u.email = None
    return u


@router.get("/users/", tags=["users"])
async def read_users():
    users = await User.all()
    return users

@router.post("/user", tags=["users"])
async def create_user(user: ModifyUser):
    try:
        u = await User.create(email = user.email, username = user.username, password = get_password_hash(user.password))
    except:
        return { "error" : "User already exist"}
    return u

@router.put("/user", tags=["users"])
async def update_user(user: ModifyProfile, response_model = UserResponse, current_user: User = Depends(require_current_user)):
    u = await User.get(id = current_user.id)
    u.fullname = user.fullname
    u.location = user.location
    u.company = user.company
    u.biography = user.biography
    await u.save()
    return u

@router.get("/me", response_model = MeResponse, tags=["users"])
async def read_current_user(response_model = UserResponse, current_user: User = Depends(require_current_user)):
    print(current_user)
    return current_user
    
@router.put("/user/{user_id}", tags=["users"])
async def edit_user(user_id : int, user: ModifyUser):
    u = User.update(user.dict()).where(User.id == user_id).execute()
    updated_u = model_to_dict(User.select().where(User.id == user_id).get())
    return updated_u

@router.delete("/me", tags=["users"])
async def delete_user(current_user: User = Depends(require_current_user)):
    u = await User.get(id = current_user.id)
    await u.delete()
    return { "status": "success" }

@router.post('/login', tags=["users"])
async def login_user(creds: Login):
    user = await User.filter(Q(username = creds.username_or_email) | Q(email = creds.username_or_email)).get()
    if not user:
        return { 'error': 'Username or email does not exist.' }
    if not verify_password(creds.password, user.password):
        return { 'error': 'Password is incorrect.' }
    if user.id >= 1:
        if is_legacy_password(user.password):
            user.password = get_password_hash(creds.password)
            user.save()
        token_data = {'id': user.id}
        token = create_access_token(token_data)

        return {'token': token, 'id': user.id, 'username': user.username}
    else:
        return {'error': 'Username or password is incorrect.'}

@router.post('/reset-password', tags=["users"])
async def create_reset_password_key(creds: ResetPasswordCreds):
    u = await User.filter(email = creds.email).get()
    if (u):
        key = await PasswordReset.create(user_id = u.id, reset_key = reset_password_key)
        #logic for emailing the key to the user goes here
        return {'status' :'success'}
    else:
        return {'error': 'Email not found.'}

