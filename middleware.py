import asyncio
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from security import Security
from auth import get_current_user

security = Security('secret_key')

async def rate_limit_middleware(request: Request, call_next):
    # Implement rate limiting logic here
    # For demonstration purposes, this function will always pass
    await asyncio.sleep(0.1)  # Simulate IO-bound operation
    response = await call_next(request)
    return response

async def authentication_middleware(request: Request, call_next):
    try:
        token = request.headers.get('Authorization')
        if token is None:
            raise HTTPException(status_code=401, detail='Missing token')
        user_id = await security.validate_token(token)
        if user_id is None:
            raise HTTPException(status_code=401, detail='Invalid token')
        response = await call_next(request)
        return response
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={'detail': e.detail})

async def input_validation_middleware(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except RequestValidationError as e:
        return JSONResponse(status_code=400, content={'detail': e.errors()})

def init_middlewares(app: FastAPI):
    app.middleware('http')(rate_limit_middleware)
    app.middleware('http')(authentication_middleware)
    app.middleware('http')(input_validation_middleware)