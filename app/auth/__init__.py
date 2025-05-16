from enum import StrEnum

from app.auth.github import github
from app.auth.google import google
from app.auth.apple import apple
from app.auth.spotify import spotify

from fastapi import APIRouter, Depends, Response
from app.auth.utils import create_access_token, create_refresh_token, get_current_user


class AuthProvider(StrEnum):
    GOOGLE = 'google'
    APPLE = 'apple'
    GITHUB = 'github'
    SPOTIFY = 'spotify'


auth = APIRouter(
    tags=['auth'],
    prefix='/auth'
)


@auth.get('/method')
async def get_auth():
    # This order will be the same order on site/app login page
    return [
        'google',
        'github',
        'spotify',
        'apple',
    ]


@auth.get('/refresh')
async def refresh(response: Response, current_user = Depends(get_current_user)):
    # Create a new access token
    access_token = create_access_token(data={"sub": current_user.username})
    response.set_cookie('access_token', access_token, httponly=True, secure=True)
    return {'msg': 'Success'}


@auth.get('/logout')
async def logout(response: Response):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return {'msg': 'Success'}


@auth.get('/verify')
async def verify(current_user = Depends(get_current_user)):
    # If we get here, the user is authenticated
    return {'msg': 'Success', 'user': current_user.username}


auth.include_router(google)
auth.include_router(apple)
auth.include_router(spotify)
auth.include_router(github)