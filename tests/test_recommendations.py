from datetime import datetime, UTC


def test_recommendations_reflect_history(client, test_db, auth_headers):
    """Test that recommendations change based on listening patterns"""
    # Get initial recommendations (before establishing pattern)
    initial_rec = client.get("/recommendations/", headers=auth_headers)
    assert initial_rec.status_code == 200, "Failed to get initial recommendations"
    initial_tracks = initial_rec.json()

    # Establish a clear listening pattern (e.g., rock genre)
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

    # Get new recommendations
    new_rec = client.get("/recommendations/", headers=auth_headers)
    assert new_rec.status_code == 200, "Failed to get updated recommendations"
    new_tracks = new_rec.json()

    # Verify recommendations have changed to reflect history
    assert initial_tracks != new_tracks, "Recommendations should change based on history"

    # Check if new recommendations have more rock tracks
    rock_count_initial = sum(1 for track in initial_tracks if "rock" in track.get("genre", "").lower())
    rock_count_new = sum(1 for track in new_tracks if "rock" in track.get("genre", "").lower())

    assert rock_count_new > rock_count_initial, "New recommendations should include more rock tracks"