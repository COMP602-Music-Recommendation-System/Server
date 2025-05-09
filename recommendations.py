from sqlalchemy.orm import Session
from app.db.models import ListeningHistory, Song
from collections import Counter


def get_recommendations_based_on_history(db: Session, user_id: int, limit: int = 10):
    """
    Generate song recommendations based on user's listening history
    """
    # Get user's listening history
    history = db.query(ListeningHistory).filter(ListeningHistory.user_id == user_id).all()

    if not history:
        # Return default recommendations if no history
        return db.query(Song).limit(limit).all()

    # Analyze favorite genres
    genres = []

    for item in history:
        song = db.query(Song).filter(Song.id == item.song_id).first()
        if song:
            genres.append(song.genre)

    # Find most common genre
    common_genre = Counter(genres).most_common(1)[0][0] if genres else None

    # Get songs with similar genre, excluding those already in history
    listened_song_ids = [item.song_id for item in history]

    if common_genre:
        recommendations = db.query(Song).filter(
            Song.id.notin_(listened_song_ids)
        ).filter(
            Song.genre == common_genre
        ).limit(limit).all()
    else:
        recommendations = db.query(Song).filter(
            Song.id.notin_(listened_song_ids)
        ).limit(limit).all()

    return recommendations