import logging
import os
from logging.handlers import RotatingFileHandler
    
def init_logger():
    log_dir = os.getenv("LOG_DIR", os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
        "logs"
    ))
    log_file = os.path.join(log_dir, "caqes.log")

    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)  

    # Get the logger for CAQES
    logger = logging.getLogger("caqes")
    
    if not logger.hasHandlers():  # Prevent adding multiple handlers
        # Set log level: Default to INFO for production, allow override via env var
        default_level = "INFO"  # Production default
        log_level = os.getenv("LOG_LEVEL", default_level).upper()
        logger.setLevel(log_level)
        
        # Formatter for logs
        formatter = logging.Formatter("%(asctime)s|%(name)s|%(levelname)s|%(message)s")

        # Rotating file handler (5MB per file, keep 5 backups)
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setFormatter(formatter)
        
        # Console logging
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Attach handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.propagate = False  # Prevent duplicate logs
