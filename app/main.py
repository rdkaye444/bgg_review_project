from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import pandas as pd
from utils.logger import setup_logger

# Set up logger
logger = setup_logger()

app = FastAPI(title="FastAPI MonsterUI App")

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Templates configuration
templates = Jinja2Templates(directory="app/templates")

# Datatypes of raw data - not likely to change.  
dtypes = {
  "ID": "Int64",                      # Unique game identifier
  "Name": "string",                   # Game title
  "Year Published": "Int64",         # Year of release
  "Min Players": "Int64",            # Minimum number of players
  "Max Players": "Int64",            # Maximum number of players
  "Play Time": "Int64",              # Average playtime in minutes
  "Min Age": "Int64",                # Minimum recommended age
  "Users Rated": "Int64",            # Number of users who rated the game
  "Rating Average": "float64",       # Average user rating (e.g. 7.8)
  "BGG Rank": "Int64",               # BoardGameGeek rank (lower is better)
  "Complexity Average": "float64",   # Average complexity rating (e.g. 2.4)
  "Owned Users": "Int64",            # Number of users who own the game
  "Mechanics": "string",             # Comma-separated game mechanics
  "Domains": "string"                # Comma-separated domains or genres
}

# Column name mapping
COLUMN_MAPPING = {
  "ID": "id",                      # Unique game identifier
  "Name": "name",                   # Game title
  "Year Published": "year_published",         # Year of release
  "Min Players": "min_players",            # Minimum number of players
  "Max Players": "max_players",            # Maximum number of players
  "Play Time": "play_time",              # Average playtime in minutes
  "Min Age": "min_age",                # Minimum recommended age
  "Users Rated": "users_rated",            # Number of users who rated the game
  "Rating Average": "rating_average",       # Average user rating (e.g. 7.8)
  "BGG Rank": "bgg_rank",               # BoardGameGeek rank (lower is better)
  "Complexity Average": "complexity_average",   # Average complexity rating (e.g. 2.4)
  "Owned Users": "owned_users",            # Number of users who own the game
  "Mechanics": "mechanics",             # Comma-separated game mechanics
  "Domains": "domains"                # Comma-separated domains or genres
}

# Load the BGG dataset
try:
    logger.info("Loading BGG dataset...")
    df = pd.read_csv('data/bgg_dataset.csv', sep=';')
    # Rename columns to use underscores
    logger.info(f"Successfully loaded {len(df)} records from BGG dataset")
    logger.debug(f"{df.dtypes}")
    logger.debug(f"{df.columns}")
    logger.debug(f"{df.head()}")


except Exception as e:
    logger.error(f"Failed to load BGG dataset: {str(e)}")
    raise

# Data Cleaning
try:
    logger.info("Cleaning Data")
    df = df.rename(columns=COLUMN_MAPPING)
    logger.debug("Columns Renamed")
    df['rating_average'] = df['rating_average'].str.replace(',','.').astype(float)
    df['complexity_average'] = df['complexity_average'].str.replace(',','.').astype(float)
    logger.debug("Converted european style commas in dataframe to decimal points")
except KeyError as e:
    logger.error("Failure during data cleaning")
    raise


@app.get("/")
async def home(request: Request):
    logger.info("Processing home page request")
    try:
        # Get some basic stats to display
        total_games = len(df)
        avg_rating = df['rating_average'].mean()
        avg_complexity = df['complexity_average'].mean()
        logger.debug(df)
        logger.debug(f"Calculated statistics: games={total_games}, avg_rating={avg_rating:.2f}, avg_complexity={avg_complexity:.2f}")
        
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "total_games": total_games,
                "avg_rating": f"{avg_rating:.2f}",
                "avg_complexity": f"{avg_complexity:.2f}",
                "recent_games": df.nlargest(5, 'users_rated')[['name', 'year_published', 'rating_average']].to_dict('records')
            }
        )
    except Exception as e:
        logger.error(f"Error processing home page request: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting FastAPI application")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 