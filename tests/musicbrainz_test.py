import logging
import os, sys
# this makes it so we can have the tests in a subdirectory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from musicbrainz_client import *


def test_find_artist():
    artist = "Taylor Swift"
    print(f"\nTesting find_artist_mbid('{artist}')...")
    mbid = find_artist_mbid(artist)
    print(f"Resulting MBID: {mbid}")
    return mbid


def test_artist_details(mbid: str):
    print(f"\nTesting get_artist_details('{mbid}')...")
    details = get_artist_details(mbid)
    print(f"Artist details (partial):")
    # Print only name and genres for reaadability
    if details:
        print(f"Name: {details.get('name')}")
        print(f"Genres: {', '.join([g.get('name') for g in details.get('genres', [])])}")
    else:
        print("No details returned.")


def test_top_tracks(mbid: str, limit: int = 5):
    print(f"\nTesting get_top_tracks_by_artist_mbid('{mbid}', limit={limit})...")
    tracks = get_top_tracks_by_artist_mbid(mbid, limit=limit)
    for i, track in enumerate(tracks, start=1):
        print(f"{i}. {track['track']} (Album: {track['album']})")


def test_tracks_by_genre(tag: str = "rock", limit: int = 5):
    print(f"\nTesting get_tracks_by_genre_tag('{tag}', limit={limit})...")
    tracks = get_tracks_by_genre_tag(tag, limit=limit)
    for i, track in enumerate(tracks, start=1):
        print(f"{i}. {track['track']} by {track['artist']} (Album: {track['album']})")


def main():
    logging.basicConfig(level=logging.INFO)
    mbid = test_find_artist()
    if mbid:
        test_artist_details(mbid)
        test_top_tracks(mbid, limit=3)
    test_tracks_by_genre(tag="jazz", limit=3)


if __name__ == "__main__":
    main()
