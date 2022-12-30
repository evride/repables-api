from fastapi import APIRouter
import subprocess

from typing import List
from fastapi import FastAPI, UploadFile, Depends, File, Form, Request
import peewee
import aiofiles
import time
from datetime import datetime

from playhouse.shortcuts import *
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from models import Item, User, Item, ItemRevision, ItemUpload, ItemView
from utils import require_current_user, get_current_user
from requests import ModifyItem, RevisionUpload
from responses import ItemResponse
router = APIRouter()


@router.get("/items/{item_id}", tags=["items"])
async def read_item(item_id: int):
    item = model_to_dict(Item.select().where(Item.id == item_id).get())
    
    images = [{
        'small': {'url': 'images/item.jpg', 'width': 310, 'height':180},
        'large': {'url': 'images/item.jpg', 'width': 620, 'height':360}
    }]
    item['previewImage'] = images[0]
    item['images'] = images
    return item
#endpoint to track item view

@router.post("/items/{item_id}/view", tags=["items"])
async def track_item_view(item_id: int, request: Request):
    current_user = await get_current_user()
    print(current_user)
    item = Item.select().where(Item.id == item_id).get()
    if item:
        ItemView.create(item_id = item_id, revision_id = item.revision_id, remote_address = request.client.host)
        return {'success' : 'true'}
    return {'error' : 'Not Found'}

@router.get("/items", response_model = List[ItemResponse], tags=["items"])
async def read_items():
    items = Item.select()
    items = [model_to_dict(item) for item in items]
    images = {
        'small': {'url': 'images/item.jpg', 'width': 310, 'height':180},
        'large': {'url': 'images/item.jpg', 'width': 620, 'height':360}
    }
    for item in items:
        item['previewImage'] = images
    return items

@router.delete("/item/{item_id}")
async def delete_item(item_id: int, current_user: User = Depends(require_current_user)):
    i = Item.select().where(Item.id == item_id).where(User.id == user_id).get()
    return i.delete_instance()
