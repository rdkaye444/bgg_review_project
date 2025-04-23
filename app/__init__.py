from .utils.logger import setup_logger
from .database import init_db
import os
import logging

# Set up logger
setup_logger()

# Then initialize database

# Initialize database and set global variables
engine, SessionLocal = init_db()

# Update the database module's globals
from . import database
database.engine = engine
database.SessionLocal = SessionLocal