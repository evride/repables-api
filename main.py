import subprocess

from fastapi import FastAPI, UploadFile, Depends, File, Form, Request
from tortoise import Tortoise, run_async

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from routers import items, item_revisions, users, explore
from config import DATABASE
from tortoise.contrib.fastapi import register_tortoise

app = FastAPI()
app.include_router(users.router)
app.include_router(items.router)
app.include_router(item_revisions.router)
app.include_router(explore.router)

db_url = "psycopg://" + DATABASE['USER'] + ':' + DATABASE['PASSWORD'] + '@' + DATABASE['HOST'] + ':' + DATABASE['PORT'] + '/' + DATABASE['NAME']

register_tortoise(
    app,
    db_url=db_url,
    modules={"models": ["models_tortoise"]},
    add_exception_handlers=True,
)

@app.get('/my-endpoint')
async def my_endpoint(request: Request):
    ip = request.client.host
    return request.client
    return {'ip': ip, 'message': 'ok'}
