from passlib.context import CryptContext
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from datetime import datetime, timedelta
from jose import jwt, JWTError
from models import User
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import Depends, HTTPException, status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# validate access token
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_reset_context = CryptContext(schemes=["sha256_crypt"])

async def get_password_hash(password):
    return pwd_context.hash(password)




async def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

async def authenticate_user(User, username_or_email: str, password: str):
    u = User.select().where(User.username == username_or_email, User.password == password).get()
    user = model_to_dict(u)
    user_hashed_password = get_password_hash(user.password)
    if not user:
        return False
    if not verify_password(password, user_hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme)):
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

