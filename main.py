import subprocess

from fastapi import FastAPI, UploadFile, Depends, File, Form, Request

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from routers import items, item_revisions, users, explore

app = FastAPI()
app.include_router(users.router)
app.include_router(items.router)
app.include_router(item_revisions.router)
app.include_router(explore.router)



@app.get('/my-endpoint')
async def my_endpoint(request: Request):
    ip = request.client.host
    return request.client
    return {'ip': ip, 'message': 'ok'}
