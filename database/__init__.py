from enum import StrEnum

from fastapi_jwt import create_access_token, AuthJWT

from auth.spotify import spotify

from fastapi import APIRouter, Depends, Response


class AuthProvider(StrEnum):

    SPOTIFY = 'spotify'


auth = APIRouter(
    tags=['auth'],
    prefix='/auth'
)


@auth.get('/method')
async def get_auth():
    # This order will be the same order on site/app login page
    return [
        'spotify',

    ]


@auth.get('/refresh')
async def refresh(response: Response, _auth: AuthJWT(True) = Depends()):
    response.set_cookie('access_token', create_access_token(auth.identity), httponly=True, secure=True)
    return {'msg': 'Success'}


@auth.get('/logout')
async def refresh(response: Response):
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    return {'msg': 'Success'}


@auth.get('/verify')
async def verify(_auth: AuthJWT() = Depends()):
    return {'msg': 'Success'}


auth.include_router(spotify)
