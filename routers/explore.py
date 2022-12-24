from fastapi import APIRouter, UploadFile, Depends, File, Form, Request
import peewee
import aiofiles
import time
from datetime import datetime

from playhouse.shortcuts import *
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from models import Item
from utils import create_access_token, get_password_hash, verify_password, require_current_user, get_current_user, reset_password_key
from requests import Login, ModifyUser, ResetKey, ResetPasswordCreds, UserResponse, MeResponse, ModifyItem, ModifyProfile, RevisionUpload

router = APIRouter()


@router.get('/search', tags=["explore"])
async def search():
    items = Item.select()
    items = [model_to_dict(item) for item in items]
    return {'results': items}