import os

from fastapi.responses import RedirectResponse
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
def login_github():
    github_authorize_url = (
        'https://github.com/login/oauth/authorize?'
        f'client_id={GITHUB_CLIENT_ID}&'
        f'redirect_uri={GITHUB_REDIRECT_URI}&'
        'scope=read:user'
    )
    return RedirectResponse(github_authorize_url)


@github.get('/')
async def auth_github(code: str):
    response = post(
        'https://github.com/login/oauth/access_token',
        headers={'Accept': 'application/json'},
        data={
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': GITHUB_REDIRECT_URI,
        },
    )
    access_token = response.json().get('access_token')
    if not access_token:
        raise HTTPException(detail='Failed to retrieve access token', status_code=400)

    user_info = get(
        'https://api.github.com/user',
        headers={'Authorization': f'token {access_token}'}
    )
    # id is GitHub’s unique identifier
    return user_info.json()
