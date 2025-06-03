from base64 import b64encode

from fastapi import APIRouter, Depends
from httpx import get

from auth import auth_jwt

profile = APIRouter(
    tags=['profile'],
    prefix='/profile'
)


@profile.get('/')
async def get_profile(_auth: auth_jwt = Depends()):
    print(_auth)
    return _auth.id


@profile.get('/avatar')
async def get_avatar(_auth: auth_jwt = Depends()):
    avatar = _auth.avatar
    if avatar is None:
        response = get(f'https://api.dicebear.com/7.x/identicon/png?seed={str(_auth.id)}')
        if response.status_code == 200:
            avatar = b64encode(response.read())
    return avatar

@profile.post('/avatar')
async def upload_avatar(_auth: auth_jwt = Depends()):
    ...
    # avatar = _auth.avatar
    # if avatar is None:
    #     response = get(f'https://api.dicebear.com/7.x/identicon/png?seed={str(_auth.id)}')
    #     if response.status_code == 200:
    #         avatar = b64encode(response.read())
    # return avatar


'https://api.dicebear.com/7.x/identicon/svg?seed=user'
