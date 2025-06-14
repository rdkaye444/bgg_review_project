from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from .database import Base

class GameNote(Base):
    __tablename__ = "game_notes"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, index=True)
    note_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class BoardGame(Base):
    __tablename__ = "board_games"

    id = Column(Integer, primary_key=True)
    bgg_id = Column(Integer, index=True)
    name = Column(String(255), index=True)
    year_published = Column(Integer)
    min_players = Column(Integer)
    max_players = Column(Integer)
    play_time = Column(Integer)
    min_age = Column(Integer)
    users_rated = Column(Integer)
    rating_average = Column(Float)
    bgg_rank = Column(Integer)
    complexity_average = Column(Float)
    owned_users = Column(Integer)
    mechanics = Column(Text)
    domains = Column(Text)
    description = Column(Text) 
    note = Column(Text)
