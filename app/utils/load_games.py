import pandas as pd
import logging
import os
from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models import BoardGame, Base
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
logger = logging.getLogger(os.getenv('LOGGER_NAME'))

def load_games_data():
    """Load board games data from CSV into the database."""
    try:
        # Create tables if they don't exist
        Base.metadata.create_all(bind=engine)
        
        # Read the CSV file
        logger.info("Reading CSV file...")
        df = pd.read_csv('app/utils/data/silver_enriched.csv')
        
        # Drop the index column if it exists
        if 'Unnamed: 0' in df.columns:
            df = df.drop('Unnamed: 0', axis=1)
        
        # Create database session
        db = SessionLocal()
        
        try:
            # First, delete existing records if any
            logger.info("Clearing existing records...")
            db.query(BoardGame).delete()
            
            # Convert DataFrame to list of dictionaries
            logger.info("Converting data for database insertion...")
            games_data = df.to_dict('records')
            
            # Insert records in batches
            batch_size = 1000
            total_records = len(games_data)
            
            for i in range(0, total_records, batch_size):
                batch = games_data[i:i + batch_size]
                # Filter out any keys that aren't in the BoardGame model
                valid_columns = BoardGame.__table__.columns.keys()
                filtered_batch = [{k: v for k, v in game.items() if k in valid_columns} for game in batch]
                game_objects = [BoardGame(**game) for game in filtered_batch]
                db.bulk_save_objects(game_objects)
                db.commit()
                logger.info(f"Inserted records {i} to {min(i + batch_size, total_records)}")
            
            logger.info(f"Successfully loaded {total_records} games into the database")
            
        except Exception as e:
            logger.error(f"Error while loading data: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Failed to load games data: {str(e)}")
        raise

if __name__ == "__main__":
    load_games_data()