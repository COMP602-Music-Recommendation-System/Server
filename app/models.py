from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

# User Model
class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)  # Ensure this is the correct field
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    history = relationship("ListeningHistory", back_populates="user")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False)

# Listening History Model
class ListeningHistory(Base):
    __tablename__ = "listening_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    song_id = Column(Integer, ForeignKey("songs.id"))
    completed = Column(Boolean, default=False)
    listened_at = Column(DateTime, default=datetime.now)

    # Relationships
    user = relationship("User", back_populates="history")
    song = relationship("Song")

# Song Model
class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    album = Column(String, nullable=True)
    genre = Column(String, nullable=True)
    duration = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

# User Preferences Model
class UserPreferences(Base):
    __tablename__ = "preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    genre_preference = Column(JSON, nullable=True)
    artist_preference = Column(JSON, nullable=True)
    language_preference = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="preferences")
