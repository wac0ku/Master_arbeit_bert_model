import logging
from rich.console import Console
from rich.progress import track
from rich.logging import RichHandler
import os

def setup_logger(module_name):
    """Set up the logger with RichHandler for enhanced console output and file logging."""
    log_dir = "Log"
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, f"{module_name}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            RichHandler(),
            logging.FileHandler(log_file, encoding='utf-8')
        ]
    )
    return logging.getLogger(module_name)

def display_progress(iterable, description="Processing"):
    """Display a progress bar using Rich."""
    for item in track(iterable, description=description):
        yield item
