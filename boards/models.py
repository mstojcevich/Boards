import datetime

from flask.ext.user import UserMixin
from sqlalchemy import Column, Integer, String, DateTime, Boolean

from boards.database import Base


class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)

    username = Column(String(50), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    reset_password_token = Column(String(100), nullable=False, default='')

    email = Column(String(255), nullable=False, unique=True)
    confirmed_at = Column(DateTime())

    active = Column('is_active', Boolean(), nullable=False, server_default='0')


class Board(Base):
    __tablename__ = 'boards'
    id = Column(Integer, primary_key=True)

    name = Column(String(32), nullable=False, unique=True)
    title = Column(String(50), nullable=False, default='Unnamed Board')
    private = Column(Boolean, nullable=False, default=False)

    sidebar_markdown = Column(String(50000), nullable=False, default='')

    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    def __init__(self, name, title, private=False):
        self.name = name
        self.title = title
        self.private = private


class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=False)
    board_id = Column(Integer, nullable=False)

    title = Column(String(128), nullable=False)
    url = Column(String(512), nullable=False)
    thumbnail = Column(String, default='/static/images/no-thumbnail.svg', nullable=False)
    posted_at = Column(DateTime, default=datetime.datetime.utcnow)

    upvotes = Column(Integer, nullable=False, default=0)
    downvotes = Column(Integer, nullable=False, default=0)

    def __init__(self, title, url, user_id, board_id):
        self.title = title
        self.url = url
        self.user_id = user_id
        self.board_id = board_id


class Moderator(Base):
    __tablename__ = 'moderators'
    id = Column(Integer, primary_key=True)

    board_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    def __init__(self, board_id, user_id):
        self.board_id = board_id
        self.user_id = user_id
