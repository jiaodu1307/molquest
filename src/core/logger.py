import logging
import sys
import yaml
from pathlib import Path
from typing import Optional

class Logger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
            cls._instance.logger = logging.getLogger("MolQuest")
            cls._instance.logger.setLevel(logging.INFO)
            cls._instance._setup_handler()
        return cls._instance

    def _setup_handler(self):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console Handler
        ch = logging.StreamHandler(sys.stdout)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)

    def configure(self, config_path: str):
        path = Path(config_path)
        if not path.exists():
            return

        with open(path, 'r') as f:
            config = yaml.safe_load(f) or {}

        level_name = None
        if isinstance(config, dict):
            logging_cfg = config.get("logging")
            if isinstance(logging_cfg, dict):
                level_name = logging_cfg.get("level")
            if not level_name:
                level_name = config.get("level")

        if not level_name:
            return

        level = getattr(logging, str(level_name).upper(), None)
        if isinstance(level, int):
            self.logger.setLevel(level)

    @classmethod
    def get_logger(cls):
        return cls().logger

def configure_logger(config_path: str) -> None:
    Logger().configure(config_path)

logger = Logger.get_logger()
