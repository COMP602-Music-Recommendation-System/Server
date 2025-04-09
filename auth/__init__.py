from fastapi import APIRouter

from auth.google import google
from auth.apple import apple

auth = APIRouter(
    tags=['auth'],
    prefix='/auth'
)

auth.include_router(google)
auth.include_router(apple)