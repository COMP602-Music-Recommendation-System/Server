from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from app.db.models import ListeningHistory, UserPreferences, User
from schemas import HistoryCreate, HistoryResponse, PreferenceUpdate, PreferenceResponse
from auth import get_current_user

router = APIRouter(
    prefix="/history",
    tags=["history"]
)


@router.post("/", response_model=HistoryResponse)
def add_to_history(
        history_item: HistoryCreate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Add a song to user's listening history"""
    new_history = ListeningHistory(
        user_id=current_user.id,
        song_id=history_item.song_id,
        completed=history_item.completed
    )
    db.add(new_history)
    db.commit()
    db.refresh(new_history)
    return new_history


@router.get("/", response_model=List[HistoryResponse])
def get_user_history(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
        skip: int = 0,
        limit: int = 100
):
    """Get current user's listening history"""
    history = db.query(ListeningHistory).filter(
        ListeningHistory.user_id == current_user.id
    ).order_by(ListeningHistory.listened_at.desc()).offset(skip).limit(limit).all()

    return history


@router.put("/preferences", response_model=PreferenceResponse)
def update_preferences(
        preferences: PreferenceUpdate,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Update user preferences"""
    user_prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()

    if not user_prefs:
        # Create new preferences if don't exist
        user_prefs = UserPreferences(user_id=current_user.id)
        db.add(user_prefs)

    # Update preferences with new values
    for key, value in preferences.dict(exclude_unset=True).items():
        setattr(user_prefs, key, value)

    db.commit()
    db.refresh(user_prefs)
    return user_prefs


@router.get("/preferences", response_model=PreferenceResponse)
def get_preferences(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Get user preferences"""
    user_prefs = db.query(UserPreferences).filter(
        UserPreferences.user_id == current_user.id
    ).first()

    if not user_prefs:

        user_prefs = UserPreferences(user_id=current_user.id)
        db.add(user_prefs)
        db.commit()
        db.refresh(user_prefs)

    return user_prefs