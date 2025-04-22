from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base

class GameNote(Base):
    __tablename__ = "game_notes"

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, index=True)
    note_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 