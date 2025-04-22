import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import URL
from dotenv import load_dotenv

logger = logging.getLogger(os.getenv("LOGGER_NAME"))

# This creates globals that are updated during init in __init__.py
engine = None
SessionLocal = None

# Load environment variables
load_dotenv()


def init_db():
    print("Setting up Logger")
    print("Log setup complete")
    # Load environment variables
    db_config_dict = {
        "username": os.getenv('DB_USERNAME', None),
        "password": os.getenv('DB_PASSWORD', None),
        "host": os.getenv('DB_HOST', "localhost"),
        "database": os.getenv('DB_NAME', "board_game_db")
    }

    print("about to log")
    logger.debug(db_config_dict)
    print("log complete")
    if not ([db_config_dict["username"], db_config_dict["password"]]):
        raise TypeError('Username and Password not specified in Environment Variables')

    db_url = URL.create("postgresql", **db_config_dict)

    try:
        db_url = URL.create("postgresql", **db_config_dict)
        logger.info("Created database URL")
        
        # Create SQLAlchemy engine
        engine = create_engine(db_url)
        logger.info("Created database engine")
        
        # Create SessionLocal class
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        logger.debug("Created session maker")
        
        return engine, SessionLocal
        
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
        raise

# Dependency to get database session
def get_db():
    if SessionLocal == None:
        raise RuntimeError('Database not initialized')
    logger.debug('Creating new session for database')
    db = SessionLocal()
    try:
        yield db
    finally:
        logger.debug('Closing database session')
        db.close()
