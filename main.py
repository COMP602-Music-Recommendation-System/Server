from auth.google import google

from fastapi.middleware.cors import CORSMiddleware
from fastapi import *

app = FastAPI(title='test', docs_url=None)

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


app.include_router(google)
