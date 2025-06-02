import logging
import os
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from . import models, schemas
from .database import get_db
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
logger=logging.getLogger(os.getenv('LOGGER_NAME'))

# Create router
router = APIRouter()

# Templates configuration
templates = Jinja2Templates(directory="app/templates")

# Load and process the BGG dataset - from the silver data
# which is enriched with descriptions
try:
    logger.info("Loading BGG dataset...")
    df = pd.read_csv('data/combined_2020.csv', sep=',')
    logger.info(f"The columns in the df are: {df.columns}")
    
except Exception as e:
    logger.error(f"Failed to load or process BGG dataset: {str(e)}")
    raise

@router.get("/")
async def home(request: Request):
    logger.info("Processing home page request")
    try:
        # Get some basic stats to display
        total_games = len(df)
        avg_rating = df['rating_average'].mean()
        avg_complexity = df['complexity_average'].mean()
        # Get all games sorted by name
        all_games = df.sort_values('rating_average')[['name', 'id']].to_dict('records')
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "total_games": total_games,
                "avg_rating": f"{avg_rating:.2f}",
                "avg_complexity": f"{avg_complexity:.2f}",
                "recent_games": df.nlargest(5, 'users_rated')[['name', 'year_published', 'rating_average']].to_dict('records'),
                "all_games": all_games
            }
        )
    except Exception as e:
        logger.error(f"Error processing home page request: {str(e)}")
        raise

@router.get("/game/{game_id}")
async def get_game_details(game_id: int):
    try:
        # Get all game details including description
        game = df[df['id'] == game_id].iloc[0].to_dict()
        # Ensure description is included (will be None if not found)
        if 'description' not in game:
            game['description'] = None
        return game
    except Exception as e:
        logger.error(f"Error fetching game details: {str(e)}")
        raise HTTPException(status_code=404, detail="Game not found")

@router.get("/game/{game_id}/notes")
async def get_game_notes(game_id: int, db: Session = Depends(get_db)):
    try:
        note = db.query(models.GameNote).filter(models.GameNote.game_id == game_id).first()
        if note is None:
            return {"note_text": ""}
        return note
    except Exception as e:
        logger.error(f"Error fetching game notes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching game notes")

@router.post("/game/{game_id}/notes")
async def save_game_notes(game_id: int, note: schemas.GameNoteCreate, db: Session = Depends(get_db)):
    try:
        existing_note = db.query(models.GameNote).filter(models.GameNote.game_id == game_id).first()
        if existing_note:
            existing_note.note_text = note.note_text
            db.commit()
            db.refresh(existing_note)
            return existing_note
        
        new_note = models.GameNote(game_id=game_id, note_text=note.note_text)
        db.add(new_note)
        db.commit()
        db.refresh(new_note)
        return new_note
    except Exception as e:
        logger.error(f"Error saving game notes: {str(e)}")
        raise HTTPException(status_code=500, detail="Error saving game notes")