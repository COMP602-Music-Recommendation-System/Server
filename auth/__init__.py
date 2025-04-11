from fastapi import APIRouter

from auth.github import github
from auth.google import google
from auth.apple import apple
from auth.spotify import spotify

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


auth.include_router(google)
auth.include_router(apple)
auth.include_router(spotify)
auth.include_router(github)
