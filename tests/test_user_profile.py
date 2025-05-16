from datetime import datetime, timedelta, UTC


def test_user_profile_shows_history(client, test_db, auth_headers):
    """Test that user profile endpoint returns listening history"""
    # 1. Add some tracks to the user's history
    track_data = [
        {
            "track_id": "rock_track_1",
            "timestamp": (datetime.now(UTC) - timedelta(days=2)).isoformat()
        },
        {
            "track_id": "pop_track_1",
            "timestamp": (datetime.now(UTC) - timedelta(days=1)).isoformat()
        },
        {
            "track_id": "jazz_track_1",
            "timestamp": datetime.now(UTC).isoformat()
        }
    ]

    for track in track_data:
        response = client.post(
            "/history/",
            headers={**auth_headers, "Content-Type": "application/json"},
            json=track
        )
        assert response.status_code in [200, 201], f"Failed to add track to history: {response.json()}"

    # 2. Get user profile
    profile_response = client.get("/profile/", headers=auth_headers)

    # 3. Check if response is successful
    assert profile_response.status_code == 200, f"Failed to get user profile: {profile_response.text}"

    # 4. Check if profile contains listening history
    profile_data = profile_response.json()
    assert "listening_history" in profile_data, "Profile should include listening history"

    # 5. Verify that all added tracks are in the history
    history_tracks = [item["track_id"] for item in profile_data["listening_history"]]
    for track in track_data:
        assert track["track_id"] in history_tracks, f"Track {track['track_id']} should be in history"


def test_user_profile_preferences(client, test_db, auth_headers):
    """Test that user profile shows preferences based on listening history"""
    # 1. Add multiple rock tracks to establish a preference
    rock_tracks = ["rock_track_1", "rock_track_2", "rock_track_3"]
    for track_id in rock_tracks:
        track_data = {
            "track_id": track_id,
            "timestamp": datetime.now(UTC).isoformat()
        }
        response = client.post(
            "/history/",
            headers={**auth_headers, "Content-Type": "application/json"},
            json=track_data
        )
        assert response.status_code in [200, 201], f"Failed to add track {track_id} to history"

    # 2. Get user profile
    profile_response = client.get("/profile/", headers=auth_headers)
    assert profile_response.status_code == 200, f"Failed to get user profile: {profile_response.text}"

    profile_data = profile_response.json()

    # 3. Check if profile contains preferences
    assert "preferences" in profile_data, "Profile should include user preferences"

    # 4. Verify that rock genre is a preference
    preferences = profile_data["preferences"]
    assert "favorite_genres" in preferences, "Preferences should include favorite genres"
    assert "Rock" in preferences["favorite_genres"], "Rock should be a favorite genre"


def test_profile_recommendations_relation(client, test_db, auth_headers):
    """Test that profile recommendations are related to user history"""
    # 1. Add some tracks to establish history
    genres = ["Rock", "Pop", "Jazz"]
    for genre in genres:
        track_id = f"{genre.lower()}_track_1"
        track_data = {
            "track_id": track_id,
            "timestamp": datetime.now(UTC).isoformat()
        }
        response = client.post(
            "/history/",
            headers={**auth_headers, "Content-Type": "application/json"},
            json=track_data
        )
        assert response.status_code in [200, 201], f"Failed to add track {track_id} to history"

    # 2. Add more rock tracks to establish stronger preference
    additional_rock = ["rock_track_2", "rock_track_3"]
    for track_id in additional_rock:
        track_data = {
            "track_id": track_id,
            "timestamp": datetime.now(UTC).isoformat()
        }
        response = client.post(
            "/history/",
            headers={**auth_headers, "Content-Type": "application/json"},
            json=track_data
        )
        assert response.status_code in [200, 201], f"Failed to add track {track_id} to history"

    # 3. Get user profile with recommendations
    profile_response = client.get("/profile/?include_recommendations=true", headers=auth_headers)
    assert profile_response.status_code == 200, f"Failed to get user profile: {profile_response.text}"

    profile_data = profile_response.json()

    # 4. Check if profile contains recommendations
    assert "recommendations" in profile_data, "Profile should include recommendations when requested"

    # 5. Check if recommendations favor rock genre (since we added more rock tracks)
    recommendations = profile_data["recommendations"]
    rock_count = sum(1 for rec in recommendations if rec.get("genre") == "Rock")
    other_count = len(recommendations) - rock_count

    assert rock_count > other_count, "Rock tracks should be recommended more often based on history"