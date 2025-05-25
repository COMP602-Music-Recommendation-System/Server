import httpx
import time
from urllib.parse import quote
import os

APP_NAME = "COMP602musicrecommendation"
APP_VERSION = "0.0.1"
CONTACT_INFO = "whollings077@gmail.com"

MUSICBRAINZ_API_BASE_URL = os.getenv('MUSICBRAINZ_API_URL', "http://10.10.10.121:5000/ws/2/")
LAST_REQUEST_TIME = 0
if "musicbrainz.org" in MUSICBRAINZ_API_BASE_URL.lower():
    REQUEST_INTERVAL = 1.1 
    print("using lower rate limit for public MusicBrainz API")
else:
    REQUEST_INTERVAL = 0.01 # seconds, for private/local server
    print("using higher rate limit for private/local MusicBrainz API")

def _make_mb_request(endpoint: str, params: dict = None, client: httpx.Client = None):
    global LAST_REQUEST_TIME
    elapsed = time.time() - LAST_REQUEST_TIME
    if elapsed < REQUEST_INTERVAL:
        time.sleep(REQUEST_INTERVAL - elapsed)

    headers = {
        "User-Agent": f"{APP_NAME}/{APP_VERSION} ({CONTACT_INFO})",
        "Accept": "application/json"
    }
    url = f"{MUSICBRAINZ_API_BASE_URL}{endpoint}"
    close_client = False
    if client is None:
        client = httpx.Client()
        close_client = True

    try:
        response = client.get(url, params=params, headers=headers, timeout=10.0)
        LAST_REQUEST_TIME = time.time()
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP error {e.response.status_code} for URL: {e.request.url}")
    except httpx.RequestError as e:
        print(f"Request error for URL: {e.request.url}")
    finally:
        if close_client:
            client.close()
    return None

#  Artist Related funcs
def find_artist_mbid(artist_name: str, client: httpx.Client = None) -> str | None:
    query = f'artist:"{artist_name}"'
    params = {"query": query, "fmt": "json", "limit": 1}
    data = _make_mb_request("artist/", params=params, client=client)
    if data and data.get("artists"):
        return data["artists"][0].get("id")
    return None

def get_artist_details(artist_mbid: str, client: httpx.Client = None) -> dict | None:
    if not artist_mbid:
        return None
    params = {"inc": "genres+tags", "fmt": "json"}
    return _make_mb_request(f"artist/{artist_mbid}", params=params, client=client)

def get_top_tracks_by_artist_mbid(artist_mbid: str, limit: int = 5, client: httpx.Client = None) -> list:
    if not artist_mbid:
        return []
    params = {"artist": artist_mbid, "fmt": "json", "limit": limit}
    data = _make_mb_request("recording/", params=params, client=client)
    tracks = []
    for rec in data.get("recordings", []):
        title = rec.get("title")
        artist = rec.get("artist-credit", [{}])[0].get("name", artist_mbid)
        album = rec.get("releases", [{}])[0].get("title", "Unknown Album")
        if title:
            tracks.append({
                "track": title,
                "artist": artist,
                "album": album,
                "mbid_track": rec.get("id"),
                "mbid_artist": artist_mbid
            })
    return tracks

# genre and tag related funcs
def get_tracks_by_genre_tag(genre_name: str, limit: int = 5, client: httpx.Client = None) -> list:
    query = f'tag:"{genre_name}"'
    params = {"query": query, "fmt": "json", "limit": limit}
    data = _make_mb_request("recording/", params=params, client=client)
    tracks = []
    for rec in data.get("recordings", []):
        title = rec.get("title")
        artist = rec.get("artist-credit", [{}])[0].get("name", "Unknown Artist")
        album = rec.get("releases", [{}])[0].get("title", "Unknown Album")
        if title:
            tracks.append({
                "track": title,
                "artist": artist,
                "album": album,
                "mbid_track": rec.get("id")
            })
    return tracks
