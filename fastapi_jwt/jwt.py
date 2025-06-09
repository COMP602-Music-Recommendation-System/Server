from datetime import datetime, timedelta, UTC
from typing import Annotated, Optional

from .config import config

from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError, DecodeError
from fastapi import Cookie, Header, Request
from fastapi.responses import JSONResponse
import jwt


class JWT:
    def __init__(
            self,
            app,
            secret_key,
            access_token_expires=timedelta(hours=1),
            refresh_token_expires=timedelta(days=1),
            bypass=False
    ):
        config['access_token_expires'] = access_token_expires
        config['refresh_token_expires'] = refresh_token_expires
        config['secret_key'] = secret_key
        config['bypass'] = bypass

        @app.exception_handler(ExpiredSignatureError)
        async def expired(*args):
            return JSONResponse({'msg': 'Token has expired'}, 401)

        @app.exception_handler(InvalidSignatureError)
        @app.exception_handler(DecodeError)
        async def invalid(*args):
            return JSONResponse({'msg': 'Signature verification failed'}, 422)

        @app.exception_handler(MissingAuthorizationCookie)
        async def missing(*args):
            return JSONResponse({'msg': 'Missing Authorization Cookie or Header'}, 401)


def __create_token(expires, identity=None, extra=None):
    payload = {
        'exp': datetime.now(UTC) + expires,
    }
    if identity:
        payload['identity'] = identity
    if extra:
        payload.update(extra)
    return jwt.encode(payload, config['secret_key'], 'HS256')


def create_access_token(identity=None, extra=None, expires: Optional[timedelta] = None):
    return __create_token(
        config['access_token_expires'] if expires is None else expires,
        identity,
        extra
    )


def create_refresh_token(identity=None):
    return __create_token(config['refresh_token_expires'], identity, {'type': 'refresh'})


def __verify_jwt(token):
    return jwt.decode(token, config['secret_key'], 'HS256')


def __verify_jwt_refresh(token):
    payload = jwt.decode(token, config['secret_key'], 'HS256')
    if 'type' not in payload or payload['type'] != 'refresh':
        raise InvalidSignatureError
    return payload


class MissingAuthorizationCookie(Exception):
    pass


def verify_jwt(token, refresh=False):
    if token:
        if refresh:
            return __verify_jwt_refresh(token)
        else:
            return __verify_jwt(token)
    else:
        raise MissingAuthorizationCookie


def verify_jwt_by_key(token, secret_key):
    token = token.split(' ')[1]
    return jwt.decode(token, secret_key, 'HS256')


class Payload:
    def __init__(self, payload):
        self.payload = payload

    @property
    def identity(self):
        return self['identity']

    def __getitem__(self, key):
        return self.payload[key]


class AuthJWT:
    def __init__(self, refresh=False):
        self.refresh = refresh

    def __call__(
            self,
            request: Request,
            access_token: Annotated[str | None, Cookie()] = None,
            refresh_token: Annotated[str | None, Cookie()] = None,
            authorization: Annotated[str | None, Header()] = None,
    ):
        if authorization:
            token = authorization.split(' ')[1]
        else:
            token = access_token
            if self.refresh:
                token = refresh_token

        if config['bypass']:
            if request.client.host in ['123.123.123.123', '127.0.0.1']:
                return Payload({'identity': 'xxxxxx'})

        return Payload(verify_jwt(token, self.refresh))
