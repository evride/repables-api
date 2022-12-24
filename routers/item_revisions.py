from fastapi import APIRouter, UploadFile, Depends, File, Form, Request
import subprocess
import peewee
import aiofiles
import time
from datetime import datetime

from playhouse.shortcuts import *
from pydantic import BaseModel
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig

from models import Item, User, Item, ItemRevision, ItemUpload, PasswordReset, ItemView
from utils import create_access_token, get_password_hash, verify_password, require_current_user, get_current_user, reset_password_key
from requests import Login, ModifyUser, ResetKey, ResetPasswordCreds, UserResponse, MeResponse, ModifyItem, ModifyProfile, RevisionUpload


router = APIRouter()

@router.post("/item-revision", tags=["item-revisions"])
async def create_item(current_user: User = Depends(require_current_user)):
    i = ItemRevision.create( user_id=current_user.id)
    return model_to_dict(i)

@router.post("/item-revision/{item_revision_id}/publish", tags=["item-revisions"])
async def publish_item( item_revision_id: int, current_user: User = Depends(require_current_user)):
    item_revision = ItemRevision.select().where(ItemRevision.id == item_revision_id).where(ItemRevision.user_id == current_user.id).get()
    existing = Item.select().where(Item.user_id == current_user.id).where(Item.revision_id == item_revision_id).get()
    if (existing):
        print(existing)
    else: 
        i = Item.create(user_id = current_user.id, revision_id = item_revision_id, name = item_revision.name, description = item_revision.description, instructions = item_revision.instructions, license = item_revision.license, version = item_revision.version ) #revision id needs to be included
        return model_to_dict(i)
        
@router.post("/item-revision/{item_revision_id}", tags=["item-revisions"])
async def update_item(item_revision_id : int, item: ModifyItem, current_user: User = Depends(require_current_user)):
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


@router.post("/file/{revision_id}", tags=["item-revisions"])
async def create_file(revision_id : str, file: UploadFile = File(...), current_user: User = Depends(require_current_user)):
    file_location = "uploaded_files/" + str(time.time())
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
            if (file_extension.lower() == 'stl'):
                subprocess.run('chromium --headless --screenshot http://render-model')

            item_upload = ItemUpload(uploader=current_user.id, revision_id = revision_id, filename = file.filename, file_location = file_location, size = size, mimetype = file.content_type, file_extension = file_extension )
            item_upload.save()
    except Exception as e:
        print(e)
    return model_to_dict(item_upload)

