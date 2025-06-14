from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class GameNoteBase(BaseModel):
    note_text: str

class GameNoteCreate(GameNoteBase):
    pass

class GameNote(GameNoteBase):
    id: int
    game_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 