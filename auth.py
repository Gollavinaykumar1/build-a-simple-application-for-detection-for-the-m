import asyncio
from security import Security
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = Security('secret_key')

async def get_current_user(token: HTTPAuthorizationCredentials = HTTPBearer()):
    user_id = await security.validate_token(token.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail='Invalid token')
    return user_id

async def authenticate_user(user_id: str, password: str):
    # Implement user authentication logic here
    # For demonstration purposes, this function will always return True
    await asyncio.sleep(1)  # Simulate IO-bound operation
    return True

async def login_user(user_id: str, password: str):
    if await authenticate_user(user_id, password):
        token = await security.generate_token(user_id)
        return token
    else:
        raise HTTPException(status_code=401, detail='Invalid credentials')