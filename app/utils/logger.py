import logging
import os
import sys
from pathlib import Path
from dotenv import load_dotenv


# Create logs directory if it doesn't exist
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
def setup_logger():
    load_dotenv()
    logger = logging.getLogger(os.getenv('LOGGER_NAME', 'bgg_app'))
    logger.setLevel(os.getenv("LOGGING_LEVEL", "INFO"))
    print(f"Logging level detected: {os.getenv('LOGGING_LEVEL')}")
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )

    # File handler
    file_handler = logging.FileHandler('logs/app.log')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger 