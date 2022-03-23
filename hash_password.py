from fastapi import FastAPI, UploadFile
import aiofiles
import time
from peewee import *

from playhouse.shortcuts import *

from config import DATABASE
from models import User, Item, ItemRevision, ItemUpload
from pydantic import BaseModel
from utils import create_access_token, get_password_hash, verify_password
app = FastAPI()



#print(get_password_hash('test'))


u = User.select().where(SQL("password NOT LIKE %s", ['$2b%']))
for user in u:
	print(user)
	user.password = get_password_hash(user.password)
	user.save()

#print(model_to_dict(u))
