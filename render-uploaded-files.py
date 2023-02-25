import subprocess

from typing import List
from fastapi import File
import peewee
import aiofiles
import time
from datetime import datetime

from playhouse.shortcuts import *

from models import Item, ItemUpload, ItemImage
from screenshot import render_model
from process_images import create_scaled_images

def getItem3dModelUploads():
    types = ["obj", "stl"]
    itemUploads = ItemUpload.disable_relationships().select().where(ItemUpload.file_extension << types).limit(0).offset(0)
    for iu in itemUploads:
        images = render_model(iu.file_location, iu.file_extension)
        for image in images:
            itemImageRow = ItemImage(revision_id=iu.revision, path=image["filename"], upload_id=iu.id, width=image["width"], height=image["height"], type=image["type"])
            itemImageRow.save()

def getItemImageUploads():
    types = ["png", "jpg", "jpeg", "bmp"]
    itemUploads = ItemUpload.disable_relationships().select().where(ItemUpload.file_extension << types).limit(10).offset(0)
    for iu in itemUploads:
        images = create_scaled_images(iu.file_location)
        for image in images:
            itemImageRow = ItemImage(revision_id=iu.revision, path=image["filename"], upload_id=iu.id, width=image["width"], height=image["height"], type=image["type"])
            itemImageRow.save()


def renderItemUploads(limit:int = 0, offset:int = 0):
    types_3d = ["obj", "stl"]
    types_img = ["png", "jpg", "jpeg", "bmp"]
    types = [*types_3d, *types_img]
    itemUploads = ItemUpload.disable_relationships().select().where(ItemUpload.revision > 1).where(ItemUpload.file_extension << types).limit(limit).offset(offset)
    for iu in itemUploads:
        if iu.file_extension in types_3d:
            images = render_model(iu.file_location, iu.file_extension)
            for image in images:
                itemImageRow = ItemImage(revision_id=iu.revision, path=image["filename"], upload_id=iu.id, width=image["width"], height=image["height"], type=image["type"])
                itemImageRow.save()
        elif iu.file_extension in types_img:
            images = create_scaled_images(iu.file_location)
            for image in images:
                itemImageRow = ItemImage(revision_id=iu.revision, path=image["filename"], upload_id=iu.id, width=image["width"], height=image["height"], type=image["type"])
                itemImageRow.save()

renderItemUploads(500, 0)

#getItem3dModelUploads(0)
#getItemImageUploads()