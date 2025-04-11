import os
from datetime import timedelta

from fastapi_jwt import JWT
from auth import auth

from fastapi.middleware.cors import CORSMiddleware
from fastapi import *

app = FastAPI(title='test', docs_url=None)
JWT(
    app,
    '07E38D73B7DF0C511753B2E6229BAE701EC6E2273FDEC78F658EDB87C81B83A3'
    '766C8BC0EA276121099BF3F609E26536EFCFD4B37FA261C5ECE1D9F2B7976DC7',
    timedelta(hours=1),
    timedelta(days=1),
    os.getenv('LOGIN_BYPASS')=='true'
)
app.add_middleware(
    CORSMiddleware,
    allow_methods=['*'],
    allow_headers=['*'],
    allow_origins=[
        'http://localhost:8100'
    ]
)


@app.get('/')
async def base():
    return 'test create'


app.include_router(auth)
