from fastapi import APIRouter, UploadFile, Depends, File, Form, Request
import peewee

from playhouse.shortcuts import *
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from models import Item
from utils import require_current_user, get_current_user
from responses import ItemResponse

router = APIRouter()


@router.get('/search', tags=["explore"])
async def search():
    items = Item.select()
    items = [model_to_dict(item) for item in items]
    return {'results': items}