import os
from fastapi import APIRouter, Depends, HTTPException
from httpx import AsyncClient, HTTPStatusError

from fastapi_jwt import AuthJWT
from auth.spotify import get_spotify_access_token_for_user

spotify_data_router = APIRouter(
    prefix="/spotify-data",
    tags=["spotify_data"]
)

SPOTIFY_API_BASE_URL = "https://api.spotify.com/v1"

@spotify_data_router.get("/top-tracks")
async def get_top_tracks(auth: AuthJWT() = Depends()):
    user_id = auth.identity # Get user ID from JWT payload
    access_token = get_spotify_access_token_for_user(user_id)

    if not access_token:
        raise HTTPException(status_code=401, detail="Spotify access token not found or expired. Please re-authenticate with Spotify.")

    async with AsyncClient() as client:
        try:
            response = await client.get(
                f"{SPOTIFY_API_BASE_URL}/me/top/tracks",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"limit": 20, "time_range": "medium_term"} # Example parameters
            )
            response.raise_for_status()
            return response.json()
        except HTTPStatusError as e:
            # Log the error e.response.text
            print(f"Spotify API Error: {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401: # Unauthorized/Expired token
                 raise HTTPException(status_code=401, detail="Spotify token is invalid or expired. Please re-authenticate.")
            elif e.response.status_code == 403: # Forbidden 
                 raise HTTPException(status_code=403, detail="Insufficient permissions to access Spotify data.")
            else:
                 raise HTTPException(status_code=500, detail="Failed to fetch data from Spotify.")
        except Exception as e:
             # Log the error e
             print(f"Unexpected error fetching Spotify data: {e}")
             raise HTTPException(status_code=500, detail="An unexpected error occurred.")