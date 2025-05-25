from collections import Counter
import httpx
import musicbrainz_client

# Configuration for recommendation algorithm
MAX_RECS_FROM_SAME_ARTIST = 2        # Max tracks per artist
MAX_RECS_FROM_GENRE = 3              # Max tracks per genre
TOTAL_RECOMMENDATIONS_TARGET = 10    # Aim for this many recommendations
TOP_N_TRACKS_FOR_ARTIST_SEEDING = 10# Consider artists from these top N tracks for seeding
TOP_N_TRACKS_FOR_GENRE_SEEDING = 20 # Consider genres from these top N tracks
MIN_GENRE_OCCURRENCE = 2 # Minimum times a genre must appear to be considered "dominant"
TOP_K_DOMINANT_GENRES = 3   # Consider this many top genres

def generate_recommendations(spotify_top_tracks: list) -> list:
    recommendations = []
    seen = set()

    if not spotify_top_tracks:
        return []

    # Seed seen set with user's current top tracks
    for t in spotify_top_tracks:
        artist = t.get("artist", "").lower()
        track = t.get("track", "").lower()
        if artist and track:
            seen.add((artist, track))

    with httpx.Client() as client:
        # Phase 1: More from same artists
        seed_artists = []
        seen_artists = set()
        for t in spotify_top_tracks[:TOP_N_TRACKS_FOR_ARTIST_SEEDING]:
            a = t.get("artist")
            if a and a.lower() not in seen_artists:
                seed_artists.append(a)
                seen_artists.add(a.lower())

        processed = {}
        for artist in seed_artists:
            if len(recommendations) >= TOTAL_RECOMMENDATIONS_TARGET:
                break

            mbid = musicbrainz_client.find_artist_mbid(artist, client=client)
            if not mbid:
                continue
            processed[artist.lower()] = {"mbid": mbid, "genres": []}

            tracks = musicbrainz_client.get_top_tracks_by_artist_mbid(
                mbid,
                limit=MAX_RECS_FROM_SAME_ARTIST + len(spotify_top_tracks),
                client=client
            )
            count = 0
            for tr in tracks:
                art_low = tr.get("artist", "").lower()
                tr_low = tr.get("track", "").lower()
                if (art_low, tr_low) not in seen and count < MAX_RECS_FROM_SAME_ARTIST:
                    if tr.get("mbid_artist") == mbid or art_low == artist.lower():
                        recommendations.append({
                            "track": tr.get("track"),
                            "artist": artist,
                            "album": tr.get("album", "Unknown Album"),
                            "reason": f"More from {artist}"
                        })
                        seen.add((art_low, tr_low))
                        count += 1
                        if len(recommendations) >= TOTAL_RECOMMENDATIONS_TARGET:
                            break

        # Phase 2: From dominant genres
        if len(recommendations) < TOTAL_RECOMMENDATIONS_TARGET:
            all_genres = []
            genre_artists = []
            seen_artists_genre = set()
            for t in spotify_top_tracks[:TOP_N_TRACKS_FOR_GENRE_SEEDING]:
                a = t.get("artist")
                if a and a.lower() not in seen_artists_genre:
                    genre_artists.append(a)
                    seen_artists_genre.add(a.lower())

            for artist in genre_artists:
                data = processed.get(artist.lower(), {})
                mbid = data.get("mbid") or musicbrainz_client.find_artist_mbid(artist, client=client)
                if mbid:
                    if not data.get("genres"):
                        details = musicbrainz_client.get_artist_details(mbid, client=client)
                        genres = details.get("genres") or details.get("tags", [])
                        genres = [g["name"].lower() for g in genres]
                        processed.setdefault(artist.lower(), {}).update({"genres": genres})
                        all_genres.extend(genres)

            if all_genres:
                counts = Counter(all_genres)
                dominant = [
                    g for g, c in counts.most_common(TOP_K_DOMINANT_GENRES * 2)
                    if c >= MIN_GENRE_OCCURRENCE
                ][:TOP_K_DOMINANT_GENRES]

                for genre in dominant:
                    if len(recommendations) >= TOTAL_RECOMMENDATIONS_TARGET:
                        break
                    tracks = musicbrainz_client.get_tracks_by_genre_tag(
                        genre,
                        limit=MAX_RECS_FROM_GENRE + len(spotify_top_tracks),
                        client=client
                    )
                    count = 0
                    for tr in tracks:
                        art_low = tr.get("artist", "").lower()
                        tr_low = tr.get("track", "").lower()
                        if (art_low, tr_low) not in seen and count < MAX_RECS_FROM_GENRE:
                            recommendations.append({
                                "track": tr.get("track"),
                                "artist": tr.get("artist"),
                                "album": tr.get("album", "Unknown Album"),
                                "reason": f"Because you like {genre.title()}"
                            })
                            seen.add((art_low, tr_low))
                            count += 1
                            if len(recommendations) >= TOTAL_RECOMMENDATIONS_TARGET:
                                break

    return recommendations
