import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    """Configure structured JSON logging for the application"""
    logger = logging.getLogger()
    
    # Prevent duplicate handlers
    if logger.handlers:
        return logger
        
    handler = logging.StreamHandler(sys.stdout)
    
    # Format logs as JSON with standard fields
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s',
        datefmt='%Y-%m-%dT%H:%M:%S',
        rename_fields={"asctime": "timestamp", "levelname": "level"}
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    
    # Set levels for third-party libs to reduce noise if needed
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING) # Optional: reduce access log noise
    
    return logger
