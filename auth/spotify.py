import os

from database import User

from fastapi_jwt import create_access_token, create_refresh_token

from fastapi.responses import RedirectResponse
from fastapi import APIRouter, HTTPException
from httpx import get, post

spotify = APIRouter(
    tags=['spotify'],
    prefix='/spotify'
)

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')


@spotify.get('/login')
async def login_spotify():
    return 'https://accounts.spotify.com/authorize?' \
           f'client_id={SPOTIFY_CLIENT_ID}&' \
           f'redirect_uri={SPOTIFY_REDIRECT_URI}&' \
           'response_type=code&' \
           'scope=user-read-email'


@spotify.get('/')
async def auth_spotify(code: str):
    if not code:
        raise HTTPException(status_code=400, detail='No code provided')

    token_response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'})

    access_token = token_response.json().get('access_token')
    if not access_token:
        raise HTTPException(detail='Failed to retrieve access token', status_code=400)

    user_info = get(
        f'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    # id is Spotify’s unique identifier
    user = User.get_by('apple_id', user_info.json()['id'])
    response = RedirectResponse(os.getenv('LOGIN_FINAL_ENDPOINT'))
    response.set_cookie('access_token', create_access_token(user.id), httponly=True, secure=True)
    response.set_cookie('refresh_token', create_refresh_token(user.id), httponly=True, secure=True)
    return response
