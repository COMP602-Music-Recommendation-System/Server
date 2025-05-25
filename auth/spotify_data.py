import os
from fastapi import APIRouter, Depends, HTTPException

import httpx
from httpx import AsyncClient, HTTPStatusError

from fastapi_jwt import AuthJWT
from auth.spotify import get_spotify_access_token_for_user

from recommendation_service import generate_recommendations

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

@spotify_data_router.get("/recommendations")
async def get_music_recommendations(auth: AuthJWT() = Depends()):
    user_id = auth.identity
    access_token = get_spotify_access_token_for_user(user_id)

    if not access_token:
        raise HTTPException(status_code=401, detail="Spotify access token not found or expired. Please re-authenticate with Spotify.") 

    spotify_top_tracks_data = []
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{SPOTIFY_API_BASE_URL}/me/top/tracks",
                headers={"Authorization": f"Bearer {access_token}"},
                params={"limit": 20, "time_range": "medium_term"}
            )
            response.raise_for_status()
            spotify_top_tracks_response = response.json()
            

            if spotify_top_tracks_response and "items" in spotify_top_tracks_response:
                for item in spotify_top_tracks_response["items"]:
                    if item.get("artists") and len(item["artists"]) > 0:
                         spotify_top_tracks_data.append({
                             "track": item.get("name"),
                             "artist": item["artists"][0].get("name") 
                         })
            
        except HTTPStatusError as e:
            print(f"Spotify API Error (recommendations - data fetch): {e.response.status_code} - {e.response.text}")
            if e.response.status_code == 401:
                 raise HTTPException(status_code=401, detail="Spotify token is invalid or expired for fetching top tracks. Please re-authenticate.")
            else:
                 raise HTTPException(status_code=500, detail="Failed to fetch top tracks from Spotify for recommendations.")
        except Exception as e:
             print(f"Unexpected error fetching Spotify top tracks for recommendations: {e}")
             raise HTTPException(status_code=500, detail="An unexpected error occurred while fetching top tracks for recommendations.")

    if not spotify_top_tracks_data:
        return {"items": [], "message": "No Spotify top tracks found to generate recommendations."}

    try:
        recommendations = generate_recommendations(spotify_top_tracks_data)
        return {"items": recommendations}
    except Exception as e:
        print(f"Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate music recommendations.")
