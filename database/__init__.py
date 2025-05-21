from uuid import uuid4

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, mapped_column

Base = declarative_base()


class PlaylistMap(Base):
    __tablename__ = 'Playlist'

    __playlist_id = Column('playlist_id', String, nullable=False, primary_key=True)
    __user_id = Column('user_id', String, ForeignKey('User.user_id'), nullable=False)


class User(Base):
    __tablename__ = 'User'

    __user_id = Column('user_id', String, nullable=False, primary_key=True)
    __username = Column('username', String, nullable=True)
    __email = Column('email', String, nullable=True)
    __spotify_id = Column('spotify_id', String, nullable=True)
    __spotify_access_token = Column('spotify_access_token', String, nullable=True)
    __spotify_refresh_token = Column('spotify_refresh_token', String, nullable=True)
    __spotify_token_expires = Column('spotify_token_expires', DateTime, nullable=True)

    playlists = relationship('PlaylistMap')

    def __init__(self):
        self.__user_id = str(uuid4())

    def __setitem__(self, key, value):
        match key:
            case 'spotify_id':
                self.__spotify_id = value
            case _:
                raise KeyError(f"Setting '{key}' via dictionary assignment is not supported or key is invalid.")

    @property
    def id(self):
        return self.__user_id
    

    @property
    def spotify_access_token(self):
        return self.__spotify_access_token

    @property
    def spotify_refresh_token(self):
        return self.__spotify_refresh_token

    @property
    def spotify_token_expires(self):
        return self.__spotify_token_expires

    @classmethod
    def get_by(cls, method: str, _id: str):
        if method not in {'user_id', 'spotify_id'}:
            raise KeyError
        user = session.query(cls).filter(getattr(cls, f'_{cls.__name__}__{method}') == _id).first()
        if user is None:
            user = User()
            session.add(user)
            user[method] = _id
        return user



db = create_engine('sqlite:///data.db', echo=False, connect_args={'timeout': 30})
Base.metadata.create_all(bind=db)
session = sessionmaker(bind=db)()