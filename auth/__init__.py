from fastapi import APIRouter

from auth.google import google
from auth.apple import apple
from auth.spotify import spotify

auth = APIRouter(
    tags=['auth'],
    prefix='/auth'
)

auth.include_router(google)
auth.include_router(apple)
auth.include_router(spotify)
