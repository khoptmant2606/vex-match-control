"""
Thread-safe event logging with timestamps and persistent disk writes.
"""
import logging
import os
import time
from common.config import LOG_DIR

class MatchLogger:
    def __init__(self, name: str = "VEX_MATCH"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%H:%M:%S")
            log_file = os.path.join(LOG_DIR, f"match_{int(time.time())}.log")
            
            fh = logging.FileHandler(log_file, encoding="utf-8")
            fh.setFormatter(formatter)
            self.logger.addHandler(fh)
            
            ch = logging.StreamHandler()
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)

    def log(self, event: str):
        self.logger.info(event)

server_logger = MatchLogger()