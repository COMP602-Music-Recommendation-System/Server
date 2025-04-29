from fastapi import APIRouter, Depends

from auth import auth_jwt

profile = APIRouter(
    tags=['profile'],
    prefix='/profile'
)


@profile.get('/')
async def get_profile(_auth: auth_jwt = Depends()):
    print(_auth)
    return
