import os
from uuid import uuid4

from sqlalchemy import create_engine, ForeignKey, Column, String, Integer, DateTime, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, mapped_column

Base = declarative_base()


class PlaylistMap(Base):
    __tablename__ = 'Playlist'

    __playlist_id = Column('playlist_id', String, nullable=False, primary_key=True)
    __user_id = Column('user_id', String, ForeignKey('User.user_id'), nullable=False)
    __playlist_name = Column('playlist_name', String, nullable=False)


class User(Base):
    __tablename__ = 'User'

    __user_id = Column('user_id', String, nullable=False, primary_key=True)
    __username = Column('username', String, nullable=True)
    __avatar = Column('avatar', String, nullable=True)

    __email = Column('email', String, nullable=True)
    __password = Column('password', String, nullable=True)
    __apple_id = Column('apple_id', String, nullable=True)
    __github_id = Column('github_id', String, nullable=True)
    __google_id = Column('google_id', String, nullable=True)
    __spotify_id = Column('spotify_id', String, nullable=True)

    playlists = relationship('PlaylistMap')

    def __init__(self):
        self.__user_id = str(uuid4())

    def __setitem__(self, key, value):
        match key:
            case 'email':
                self.__email = value
            case 'apple_id':
                self.__apple_id = value
            case 'github_id':
                self.__github_id = value
            case 'google_id':
                self.__google_id = value
            case 'spotify_id':
                self.__spotify_id = value
            case 'username':
                self.__username = value
            case 'password':
                self.__password = value
            case 'user_id':
                self.__user_id = value
            case _:
                raise KeyError
        session.commit()

    @property
    def id(self):
        return self.__user_id

    @property
    def avatar(self):
        return self.__avatar


    @classmethod
    def get_by(cls, method: str, _id: str):
        if method not in ('email', 'user_id', 'apple_id', 'github_id', 'google_id', 'spotify_id'):
            raise KeyError
        user = session.query(cls).filter(getattr(cls, f'_{cls.__name__}__{method}') == _id).first()
        if user is None:
            user = User()
            session.add(user)
            user[method] = _id
        return user


# TODO: Temporary value and file name
db = create_engine(f'sqlite:///{os.getenv('DB_PATH')}', echo=False, connect_args={'timeout': 30})
Base.metadata.create_all(bind=db)
session = sessionmaker(bind=db)()
