import logging
import os
from logging.handlers import RotatingFileHandler

class WorkerIDFilter(logging.Filter):
    def __init__(self, worker_id):
        super().__init__()
        self.worker_id = worker_id

    def filter(self, record):
        record.worker_id = self.worker_id
        return True
    
def get_worker_logger(worker_id=None):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, "logs")
    log_file = os.path.join(log_dir, "caqes.log")

    # Ensure logs directory exists
    os.makedirs(log_dir, exist_ok=True)  

    # Get the logger for CAQES
    logger = logging.getLogger("caqes")
    
    if not logger.hasHandlers():  # Prevent adding multiple handlers
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())  # Default to INFO
        
        # Formatter for logs
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

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

def get_worker_logger(worker_id=None):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    log_dir = os.path.join(project_root, "logs")
    log_file = os.path.join(log_dir, "caqes.log")

    os.makedirs(log_dir, exist_ok=True)

    logger = logging.getLogger(f"caqes.worker-{worker_id if worker_id else ''}")
    
    if not logger.hasHandlers():
        logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
        
        # Modified formatter to include worker_id
        formatter = logging.Formatter(
            "%(asctime)s - [%(worker_id)s] - %(levelname)s - %(message)s"
        )

        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5)
        file_handler.setFormatter(formatter)
        
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # Add the worker ID filter
        if worker_id is not None:
            worker_filter = WorkerIDFilter(worker_id)
            file_handler.addFilter(worker_filter)
            console_handler.addFilter(worker_filter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        logger.propagate = False
    
    return logger