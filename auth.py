import time
import hashlib
from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta
from jose import jwt, JWTError
from models import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status, Request
from playhouse.shortcuts import model_to_dict

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# validate access token
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_reset_context = CryptContext(schemes=["sha256_crypt"])
reset_password_key = str(pwd_reset_context.hash(str(time.time())).replace('.', '').replace('/', '').split('$')[-1])[:32]

def get_password_hash(password: str):
    return str(pwd_context.hash(password))



def is_legacy_password(hashed_password):
    return hashed_password[0:3] == '$00'

def verify_password(plain_password, hashed_password):
    if is_legacy_password(hashed_password):
        return verify_legacy_password(plain_password, hashed_password)
    else:
        return pwd_context.verify(plain_password, hashed_password)

def verify_legacy_password(plain_password, hashed_password):
    password_split = hashed_password[4:].split('/')
    salt = password_split[0]
    password_hash = password_split[1]
    username = password_split[2]

    m = hashlib.sha256()
    m.update(str(username + plain_password + salt).encode())
    password_check_hash = m.hexdigest()
    return password_check_hash == password_hash

async def authenticate_user(username_or_email: str, password: str):
    user = User.select().where(User.username == username_or_email, User.password == password).get()
    user_hashed_password = get_password_hash(user.password)
    if not user:
        return False
    if not verify_password(password, user_hashed_password):
        return False
    return user

async def require_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        if id is None:
            raise credentials_exception
        token_data = {'id' : id}
    except JWTError:
        raise credentials_exception
    user = User.select().where(User.id == token_data['id']).get()
    if user is None:
        raise credentials_exception
    return user

async def get_current_user(request: Request):
    token = await oauth2_scheme(request)
    try:
        user = await require_current_user(token)
    except HTTPException:
        print("dude")
        return {"id": -1}
    return model_to_dict(user)
async def get_current_user2(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        token_data = {'id' : id}
    except JWTError:
        return {"id": -1}
    user = User.select().where(User.id == token_data['id']).get()
    return user