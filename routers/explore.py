from fastapi import APIRouter, UploadFile, Depends, File, Form, Request
import peewee

from playhouse.shortcuts import *
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from models import Item
from utils import require_current_user, get_current_user
from responses import PaginatedSearchResponse

router = APIRouter()

@router.get("/search", response_model = PaginatedSearchResponse, tags=["explore"])
async def search(q:str = "", offset:int = 0, limit: int = 20):
    query = "%" + q + "%"
    limit = min(max(limit, 1), 100)    
    itemCount = Item.select().where(
        (Item.name ** query)
    ).count()
    items = Item.select().where(
        (Item.name ** query)
    ).limit(limit).offset(offset)
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
    return { 'q': q, 'offset': offset, 'limit': limit, 'count': itemCount, 'results': items }