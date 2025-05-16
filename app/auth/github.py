import os

from app.models import User

from fastapi import APIRouter, HTTPException
from httpx import get, post

github = APIRouter(
    tags=['github'],
    prefix='/github'
)

GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI')


@github.get('/login')
async def login_github():
    return 'https://github.com/login/oauth/authorize?' \
           f'client_id={GITHUB_CLIENT_ID}&' \
           f'redirect_uri={GITHUB_REDIRECT_URI}&' \
           'scope=read:user'


@github.get('/')
async def auth_github(code: str):
    token_response = post(
        'https://github.com/login/oauth/access_token',
        headers={'Accept': 'application/json'},
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': GITHUB_REDIRECT_URI,
        },
    )
    access_token = token_response.json().get('access_token')
    if not access_token:
        raise HTTPException(detail='Failed to retrieve access token', status_code=400)

    user_info = get(
        'https://api.github.com/user',
        headers={'Authorization': f'token {access_token}'}
    )
    # id is GitHub’s unique identifier
    user = User.get_by('github_id', user_info.json()['id'])
    response = RedirectResponse(os.getenv('LOGIN_FINAL_ENDPOINT'))
    response.set_cookie('access_token', create_access_token(user.id), httponly=True, secure=True)
    response.set_cookie('refresh_token', create_refresh_token(user.id), httponly=True, secure=True)
    return response
