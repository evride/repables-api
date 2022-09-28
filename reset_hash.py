from passlib.context import CryptContext
import time

pwd_reset_context = CryptContext(schemes=["sha256_crypt"])
reset_password_key = str(pwd_reset_context.hash(str(time.time())).replace('.', '').replace('/', '').split('$')[-1])[:32]

