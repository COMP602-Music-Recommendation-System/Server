# Steps for Running the Project

Follow these steps to set up and run the project locally.

---

## 1. Create a `.env` File

A `.env` file is required in your project root. Copy the following template and fill in the blanks.
If you need values, ask **William** on Teams.

<details>
<summary><strong>.env Template</strong> (click to expand)</summary>

```env
# Frontend login final endpoint (change if needed)
LOGIN_FINAL_ENDPOINT="http://localhost:8100/#/login"

# Leave this as is (legacy setting)
LOGIN_BYPASS=false

# Spotify Developer credentials
SPOTIFY_REDIRECT_URI="http://localhost:8000/auth/spotify"
SPOTIFY_CLIENT_ID="your_spotify_client_id_here"
SPOTIFY_CLIENT_SECRET="your_spotify_client_secret_here"

# MusicBrainz API endpoint
# comment below out if using a self-hosted replica for higher rate limits
MUSICBRAINZ_API_URL="https://musicbrainz.org/ws/2/"
```

</details>

---

## 2. Install Dependencies

Make sure you have the needed requirements installed.

```bash
pip install -r requirements.txt
```

---

## 3. Run the Project

Start the backend server with:

```bash
uvicorn start:app --reload
```

This will launch the API with live-reload enabled on code changes.


