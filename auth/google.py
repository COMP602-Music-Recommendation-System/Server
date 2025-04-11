import os

from fastapi.responses import RedirectResponse
from fastapi import APIRouter
from httpx import post, get

google = APIRouter(
    tags=['auth', 'google'],
    prefix='/google'
)

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
GOOGLE_REDIRECT_URI = os.getenv('GOOGLE_REDIRECT_URI')


@google.get('/login')
async def login_google():
    return RedirectResponse(
        'https://accounts.google.com/o/oauth2/auth?response_type=code&'
        f'client_id={GOOGLE_CLIENT_ID}&'
        f'redirect_uri={GOOGLE_REDIRECT_URI}&'
        'scope=openid%20profile%20email&access_type=offline'
    )


@google.get('/')
async def auth_google(code: str):
    response = post('https://accounts.google.com/o/oauth2/token', data={
        'code': code,
        'client_id': GOOGLE_CLIENT_ID,
        'client_secret': GOOGLE_CLIENT_SECRET,
        'redirect_uri': GOOGLE_REDIRECT_URI,
        'grant_type': 'authorization_code',
    })
    user_info = get(
        'https://www.googleapis.com/oauth2/v1/userinfo',
        headers={'Authorization': f"Bearer {response.json().get('access_token')}"}
    )
    return user_info.json()
