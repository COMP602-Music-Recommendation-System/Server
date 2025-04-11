from time import time
import os

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
def login_apple():
    return RedirectResponse(
        'https://appleid.apple.com/auth/authorize?'
        f'client_id={APPLE_CLIENT_ID}&'
        f'redirect_uri={APPLE_REDIRECT_URI}&'
        'scope=name email&'
        'response_type=code&'
        'response_mode=form_post'
    )


@apple.post('/')
async def auth_apple(request: Request):
    form = await request.form()
    code = form.get("code")

    with open(APPLE_PRIVATE_KEY_PATH, 'r') as file:
        private_key = file.read()

    client_secret = jwt.encode(
        {
            'iss': APPLE_TEAM_ID,
            'iat': int(time()),
            'exp': int(time()) + 86400 * 180,
            'aud': 'https://appleid.apple.com',
            'sub': APPLE_CLIENT_ID,
        }, private_key,
        headers={
            'alg': 'ES256',
            'kid': APPLE_KEY_ID,
        },
        algorithm='ES256'
    )

    data = {
        'client_id': APPLE_CLIENT_ID,
        'client_secret': client_secret,
        'code': code,
        'grant_type': 'authorization_code',
        'redirect_uri': APPLE_REDIRECT_URI,
    }

    response = post('https://appleid.apple.com/auth/token', data=data)

    id_token = response.json().get('id_token')
    if not id_token:
        raise HTTPException(status_code=400, detail='Failed to retrieve ID token')
    decoded_token = jwt.decode(id_token, options={'verify_signature': False})
    # sub is Apple’s unique identifier
    return decoded_token
