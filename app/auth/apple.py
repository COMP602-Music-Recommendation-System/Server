from time import time
import os

from app.models import User
from app.auth.utils import create_access_token, create_refresh_token
from app.auth.utils import create_access_token

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from httpx import post
import jwt

apple = APIRouter(
    tags=['apple'],
    prefix='/apple'
)

APPLE_PRIVATE_KEY_PATH = os.getenv('APPLE_PRIVATE_KEY_PATH')
APPLE_REDIRECT_URI = os.getenv('APPLE_REDIRECT_URI')
APPLE_CLIENT_ID = os.getenv('APPLE_CLIENT_ID')
APPLE_TEAM_ID = os.getenv('APPLE_TEAM_ID')
APPLE_KEY_ID = os.getenv('APPLE_KEY_ID')


@apple.get('/login')
async def login_apple():
    return 'https://appleid.apple.com/auth/authorize?' \
           f'client_id={APPLE_CLIENT_ID}&' \
           f'redirect_uri={APPLE_REDIRECT_URI}&' \
           'scope=name email&' \
           'response_type=code&' \
           'response_mode=form_post'


@apple.post('/')
async def auth_apple(request: Request):
    form = await request.form()
    code = form.get("code")

    with open(APPLE_PRIVATE_KEY_PATH, 'r') as file:
        private_key = file.read()

    token_response = post('https://appleid.apple.com/auth/token', data={
        'client_id': APPLE_CLIENT_ID,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': APPLE_REDIRECT_URI,
        'client_secret': jwt.encode(
            {
                'iss': APPLE_TEAM_ID,
                'iat': int(time()),
                'exp': int(time()) + 86_400,
                'aud': 'https://appleid.apple.com',
                'sub': APPLE_CLIENT_ID,
            }, private_key,
            headers={
                'alg': 'ES256',
                'kid': APPLE_KEY_ID,
            },
            algorithm='ES256'
        )
    })

    id_token = token_response.json().get('id_token')
    if not id_token:
        raise HTTPException(status_code=400, detail='Failed to retrieve ID token')

    user_info = jwt.decode(id_token, options={'verify_signature': False})
    # sub is Apple’s unique identifier
    user = User.get_by('apple_id', user_info['sub'])
    response = RedirectResponse(os.getenv('LOGIN_FINAL_ENDPOINT'))
    response.set_cookie('access_token', create_access_token(user.id), httponly=True, secure=True)
    response.set_cookie('refresh_token', create_refresh_token(user.id), httponly=True, secure=True)
    return response

