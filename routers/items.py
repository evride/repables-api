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
from requests import ModifyItem, RevisionUpload, PageRequest
from responses import PaginatedItemsResponse
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

@router.get("/items", response_model = PaginatedItemsResponse, tags=["items"])
async def read_items(offset:int = 0, limit: int = 20):
    limit = min(max(limit, 1), 100)    
    itemCount = Item.select().count()
    items = Item.select().limit(limit).offset(offset)
    items = [model_to_dict(item) for item in items]
    images = {
        'small': {'url': 'images/item.jpg', 'width': 310, 'height':180},
        'large': {'url': 'images/item.jpg', 'width': 620, 'height':360}
    }
    for item in items:
        if item['id'] % 3 == 0:
            item['previewImage'] = {
                'small': {'url': 'images/item.jpg', 'width': 310, 'height':180},
                'large': {'url': 'images/item.jpg', 'width': 620, 'height':360}
            }
        if item['id'] % 3 == 1:
            item['previewImage'] = {
                'small': {'url': 'images/gallery/feab05aa91085b7a8012516bc3533958_7840b37940929118b62a0a25fda34951_thumb.jpg', 'width': 110, 'height':64},
                'large': {'url': 'images/gallery/feab05aa91085b7a8012516bc3533958_7840b37940929118b62a0a25fda34951.jpg', 'width': 620, 'height':360}
            }
        if item['id'] % 3 == 2:
            item['previewImage'] = {
                'small': {'url': 'images/gallery/f63f65b503e22cb970527f23c9ad7db1_1aa8564e5646169a4f7b792efff84641_thumb.jpg', 'width': 110, 'height':64},
                'large': {'url': 'images/gallery/f63f65b503e22cb970527f23c9ad7db1_1aa8564e5646169a4f7b792efff84641.jpg', 'width': 620, 'height':360}
            }
    return { 'offset': offset, 'limit': limit, 'count': itemCount, 'results': items }

@router.delete("/item/{item_id}")
async def delete_item(item_id: int, current_user: User = Depends(require_current_user)):
    i = Item.select().where(Item.id == item_id).where(User.id == user_id).get()
    return i.delete_instance()
