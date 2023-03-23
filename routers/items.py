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

from models_tortoise import Item, User, ItemRevision, ItemUpload, ItemView, ItemLike
from auth import require_current_user, get_current_user
from requests import ModifyItem, RevisionUpload, PageRequest, LikePost
from responses import PaginatedItemsResponse, ItemResponse
from query_records import getItemsRevisionImages, getItemRevisionsImages
router = APIRouter()

@router.get("/items/{item_id}", response_model = ItemResponse, response_model_exclude_none=True, tags=["items"])
async def read_item(item_id: int):

    item = getItemRevisionsImages(item_id)
    return item
#endpoint to track item view

@router.post("/items/{item_id}/view", tags=["items"])
async def track_item_view(item_id: int, request: Request):
    current_user = await get_current_user(request)
    item = await Item.get(id = item_id)
    likingUser = current_user.id if current_user != None else None
    if item:
        await ItemView.create(item_id = item_id, revision_id = 215, user_id = likingUser, remote_address = request.client.host)
        return {'success' : 'true'}
    return {'error' : 'Not Found'}

@router.post("/items/{item_id}/like", tags=["items"])
async def track_item_like(item_id: int, likePost: LikePost, request: Request, current_user: User = Depends(require_current_user)):
    item = await Item.get(id = item_id)
    print(item)
    if item:
        #ItemLike.create(item_id = item_id, revision_id = item.revision_id, score:  remote_address = request.client.host)
        await ItemLike.create(item_id = item_id, user_id = current_user.id, score = likePost.score, remote_address = request.client.host)
        
        item.item_likes = item.item_likes + 1
        await item.save()       
        
        return {'success' : 'true'}
    return {'error' : 'Not Found'}

@router.get("/items", response_model = PaginatedItemsResponse, response_model_exclude_none=True, tags=["items"])
async def read_items(offset:int = 0, limit: int = 20):
    limit = min(max(limit, 1), 100)

    response = getItemsRevisionImages(limit, offset)
    
    return { 'offset': offset, 'limit': limit, 'count': response['count'], 'results': response['results'] }

@router.delete("/item/{item_id}")
async def delete_item(item_id: int, current_user: User = Depends(require_current_user)):
    i = await Item.get(id = item_id)
    await i.delete()
    return {"success": True}


