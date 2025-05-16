import time
from datetime import datetime, UTC  # Import UTC for timezone-aware objects


def test_history_persistence(client, test_db, auth_headers):
    """Test that history persists between sessions"""
    # Generate a unique track ID for this test
    unique_track = f"test_track_{int(time.time())}"

    # Add this track to history
    track_data = {
        "track_id": unique_track,
        "timestamp": datetime.now(UTC).isoformat()  # Use timezone-aware datetime
    }

    add_response = client.post(
        "/history/",
        headers={**auth_headers, "Content-Type": "application/json"},
        json=track_data
    )
    assert add_response.status_code in [200, 201], f"Failed to add track to history: {add_response.text}"

    # Create a new session (simulate restart by getting a new token)
    login_response = client.post(
        "/token",
        data={"username": "test_user", "password": "test_password"}
    )
    assert login_response.status_code == 200, f"Failed to login: {login_response.text}"

    new_token = login_response.json()["access_token"]
    new_headers = {"Authorization": f"Bearer {new_token}"}

    # Get history after "restart"
    history_response = client.get("/history/", headers=new_headers)

    # Debug information if the request fails
    if history_response.status_code != 200:
        print(f"History response error: {history_response.status_code}")
        print(f"Response body: {history_response.text}")

    assert history_response.status_code == 200, f"Failed to get history: {history_response.text}"

    history_items = history_response.json()

    # Verify our unique track is in the history
    found = any(item["track_id"] == unique_track for item in history_items)
    assert found, f"Unique track {unique_track} not found in history after simulated restart"