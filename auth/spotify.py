import os
from datetime import datetime, timedelta, timezone
from httpx import get, post, HTTPStatusError

from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from fastapi_jwt import create_access_token, create_refresh_token

from database import User, session

from dotenv import load_dotenv

load_dotenv() # load from .env

spotify = APIRouter(
    tags=['spotify'],
    prefix='/spotify'
)

#load environment variables
SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')
SPOTIFY_REDIRECT_URI = os.getenv('SPOTIFY_REDIRECT_URI')
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
LOGIN_FINAL_ENDPOINT = os.getenv('LOGIN_FINAL_ENDPOINT', '/') # Default to root if not set

# Spotify API Endpoints
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_USER_INFO_URL = "https://api.spotify.com/v1/me"


@spotify.get('/login')
async def login_spotify():
    # Scopes required for basic info and top tracks
    scopes = "user-read-email user-top-read"
    # Construct the authorization URL
    auth_url = (
        f"{SPOTIFY_AUTH_URL}?"
        f"client_id={SPOTIFY_CLIENT_ID}&"
        f"redirect_uri={SPOTIFY_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope={scopes}"
    )
    # Redirect the user to Spotify for authorization
    return {"authorization_url": auth_url}


@spotify.get('/')
async def auth_spotify(code: str | None = None, error: str | None = None):
    if error:
        raise HTTPException(status_code=400, detail=f"Spotify authorization error: {error}")
    if not code:
        raise HTTPException(status_code=400, detail='No authorization code provided by Spotify')
    try:
        token_response = post(SPOTIFY_TOKEN_URL, data={
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': SPOTIFY_REDIRECT_URI,
            'client_id': SPOTIFY_CLIENT_ID,
            'client_secret': SPOTIFY_CLIENT_SECRET,
        }, headers={'Content-Type': 'application/x-www-form-urlencoded'})

        token_response.raise_for_status()
        token_data = token_response.json()

    except HTTPStatusError as e:
        # Log the detailed error from spotify (for troubleshooting)
        print(f"Spotify Token Exchange Error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"Failed to exchange code for token: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error during token exchange: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error during Spotify token exchange.")

    # Extract token details
    access_token = token_data.get('access_token')
    refresh_token = token_data.get('refresh_token')
    expires_in = token_data.get('expires_in') # Duration in seconds

    if not access_token:
        raise HTTPException(status_code=400, detail='Failed to retrieve access token from Spotify response')

    # Fetch user info from Spotify 
    try:
        user_info_response = get(
            SPOTIFY_USER_INFO_URL,
            headers={'Authorization': f'Bearer {access_token}'}
        )
        user_info_response.raise_for_status()
        user_info = user_info_response.json()
    except HTTPStatusError as e:
         print(f"Spotify User Info Error: {e.response.status_code} - {e.response.text}")
         raise HTTPException(status_code=e.response.status_code, detail=f"Failed to fetch user info from Spotify: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error fetching user info: {e}")
        raise HTTPException(status_code=500, detail="Unexpected error fetching Spotify user info.")

    # get spotify user ID from the response
    spotify_user_id = user_info.get('id')
    if not spotify_user_id:
        raise HTTPException(status_code=500, detail="Could not get user ID from Spotify profile")

    # get or create user in the database
    try:
        user = User.get_by('spotify_id', spotify_user_id)
        # Update user's Spotify tokens and expiry time
        user._User__spotify_access_token = access_token
        if refresh_token: # update refresh token if provided
            user._User__spotify_refresh_token = refresh_token
        if expires_in:
            # Calculate expiry time using UTC timezone
            user._User__spotify_token_expires = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
        else:
             # case where expires_in is missing
             user._User__spotify_token_expires = None

        # Commit changes to the database session
        session.commit()

    except HTTPException:
         raise
    except Exception as e:
        print(f"Database Error saving tokens for spotify_id {spotify_user_id}: {e}")
        session.rollback() # Rollback transaction on error
        raise HTTPException(status_code=500, detail="Failed to save user token information.")
    #create JWTs for the user
    try:
        app_access_token = create_access_token(user.id)
        app_refresh_token = create_refresh_token(user.id)
    except Exception as e:
        # Handle potential errors during JWT creation
        print(f"Error creating JWTs for user {user.id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to create authentication tokens.")
    response = RedirectResponse(LOGIN_FINAL_ENDPOINT)

    # Simple check for localhost
    is_secure = not ("localhost" in SPOTIFY_REDIRECT_URI or "127.0.0.1" in SPOTIFY_REDIRECT_URI)

    # Set access token cookie
    response.set_cookie(
        key='access_token',
        value=app_access_token,
        httponly=True,
        samesite='lax',
        path='/',
        secure=is_secure
    )
    # Set refresh token cookie
    response.set_cookie(
        key='refresh_token',
        value=app_refresh_token,
        httponly=True,
        samesite='lax',
        path='/',
        secure=is_secure
    )

    return response

def get_spotify_access_token_for_user(user_id: str) -> str | None:
    if not user_id:
        print("Error: No user_id provided to get_spotify_access_token_for_user.")
        return None

    try:
        user = session.query(User).filter(User._User__user_id == user_id).first()

        if not user:
            print(f"User with ID {user_id} not found in the database.")
            return None
        if not user.spotify_access_token:
            print(f"User {user_id} found, but no initial Spotify access token stored.")
            return None # No token to check or refresh
        token_expires_aware = user.spotify_token_expires
        is_expired = True # Default to expired

        if token_expires_aware:
            # Ensure the stored time is timezone-aware (assume UTC if naive)
            if token_expires_aware.tzinfo is None:
                 # Log this occurrence, might indicate DB storage issue
                 print(f"Warning: Retrieved naive datetime for user {user_id}, assuming UTC.")
                 token_expires_aware = token_expires_aware.replace(tzinfo=timezone.utc)

            # Check if expiry time is more than 5 minutes in the future
            if token_expires_aware > (datetime.now(timezone.utc) + timedelta(minutes=5)):
                 is_expired = False

        if not is_expired:
            print(f"Spotify token for user {user_id} is still valid.")
            return user.spotify_access_token # Return the existing valid token
        #token refresh-
        print(f"Spotify token for user {user_id} needs refresh.")
        if not user.spotify_refresh_token:
            print(f"Cannot refresh Spotify token for user {user_id}: No refresh token available.")
            return None

        print(f"Attempting to refresh Spotify token for user {user_id}...")
        try:
            refresh_response = post(SPOTIFY_TOKEN_URL, data={
                'grant_type': 'refresh_token',
                'refresh_token': user.spotify_refresh_token,
                'client_id': SPOTIFY_CLIENT_ID,
                'client_secret': SPOTIFY_CLIENT_SECRET,
            }, headers={'Content-Type': 'application/x-www-form-urlencoded'})

            refresh_response.raise_for_status() # Check for HTTP errors
            token_data = refresh_response.json()

            new_access_token = token_data.get('access_token')
            new_expires_in = token_data.get('expires_in')
            # Spotify might return a new refresh token, update if it does
            new_refresh_token = token_data.get('refresh_token')

            if not new_access_token or new_expires_in is None: # Check expires_in explicitly
                 # Log the failure reason
                 print(f"Failed to refresh token for user {user_id}: Invalid response from Spotify - {token_data}")
                 return None # Indicate refresh failure

            # Update user record in the database
            print(f"Updating database with new Spotify token for user {user_id}")
            user._User__spotify_access_token = new_access_token
            user._User__spotify_token_expires = datetime.now(timezone.utc) + timedelta(seconds=new_expires_in)
            if new_refresh_token:
                 print(f"Received and updating new refresh token for user {user_id}")
                 user._User__spotify_refresh_token = new_refresh_token

            session.commit() # Save changes to the database
            print(f"Successfully refreshed and saved Spotify token for user {user_id}")
            return new_access_token

        except HTTPStatusError as e:
            print(f"HTTP Error refreshing Spotify token for user {user_id}: {e.response.status_code} - {e.response.text}")
            session.rollback() # Rollback database changes on error

            # If refresh token is invalid (common 400/401 errors), clear stored tokens
            if e.response.status_code in [400, 401]:
                 print(f"Clearing invalid Spotify tokens for user {user_id} due to refresh error.")
                 user._User__spotify_access_token = None
                 user._User__spotify_refresh_token = None
                 user._User__spotify_token_expires = None
                 try:
                     session.commit()
                 except Exception as db_err:
                     print(f"Database error while clearing tokens for user {user_id}: {db_err}")
                     session.rollback()
            return None # Indicate refresh failure
        except Exception as e:
            # Log any other unexpected errors during refresh
            print(f"Unexpected error during Spotify token refresh for user {user_id}: {e}")
            session.rollback()
            return None # Indicate refresh failure

    except Exception as e:
        print(f"Error retrieving/processing token for user {user_id}: {e}")
        session.rollback() # Rollback if any session changes occurred
        return None