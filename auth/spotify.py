import os

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
def login_spotify():
    return RedirectResponse(
        'https://accounts.spotify.com/authorize?'
        f'client_id={SPOTIFY_CLIENT_ID}&'
        f'redirect_uri={SPOTIFY_REDIRECT_URI}&'
        'response_type=code&'
        'scope=user-read-email'
    )


@spotify.get('/')
async def callback(code: str):
    if not code:
        raise HTTPException(status_code=400, detail='No code provided')

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': SPOTIFY_REDIRECT_URI,
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET,
    }, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    access_token = response.json().get('access_token')

    if not access_token:
        raise HTTPException(detail='Failed to retrieve access token', status_code=400)

    # Get user profile
    user_info = get(
        f'https://api.spotify.com/v1/me',
        headers={'Authorization': f'Bearer {access_token}'}
    )
    return user_info.json()
