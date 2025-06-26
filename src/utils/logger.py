import logging
import logging.handlers
from datetime import datetime
import json
import traceback

class AtlasLogger:
    def __init__(self, name: str, log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))

        # Ротаційні файли логів
        handler = logging.handlers.RotatingFileHandler(
            f"logs/{name}.log",
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_with_context(self, level: str, message: str, context: dict = None):
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "context": context or {},
            "traceback": traceback.format_exc() if level == "ERROR" else None
        }
        getattr(self.logger, level.lower())(json.dumps(log_entry))