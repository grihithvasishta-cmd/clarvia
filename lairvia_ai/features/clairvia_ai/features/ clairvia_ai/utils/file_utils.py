import logging
from pathlib import Path
from typing import Optional
import json
import os

logger = logging.getLogger(__name__)

class FileHandler:
    """Utility functions for file operations"""
    
    def __init__(self):
        self.logger = logger
    
    def read_text(self, path: str) -> Optional[str]:
        try:
            p = Path(path)
            if not p.exists():
                self.logger.error(f"File not found: {path}")
                return None
            content = p.read_text(encoding='utf-8')
            return content
        except Exception as e:
            self.logger.error(f"Error reading text file {path}: {e}")
            return None
    
    def write_text(self, path: str, content: str) -> bool:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(content, encoding='utf-8')
            return True
        except Exception as e:
            self.logger.error(f"Error writing text file {path}: {e}")
            return False
    
    def save_json(self, path: str, obj) -> bool:
        try:
            p = Path(path)
            p.parent.mkdir(parents=True, exist_ok=True)
            with p.open('w', encoding='utf-8') as f:
                json.dump(obj, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            self.logger.error(f"Error saving json {path}: {e}")
            return False
    
    def load_json(self, path: str):
        try:
            p = Path(path)
            if not p.exists():
                self.logger.error(f"JSON file not found: {path}")
                return None
            with p.open('r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading json {path}: {e}")
            return None
    
    def ensure_dir(self, path: str):
        try:
            Path(path).mkdir(parents=True, exist_ok=True)
        except Exception as e:
            self.logger.error(f"Error creating directory {path}: {e}")
    
    def list_files(self, directory: str, pattern: str = "*") -> list:
        try:
            p = Path(directory)
            if not p.exists():
                return []
            return [str(x) for x in p.glob(pattern)]
        except Exception as e:
            self.logger.error(f"Error listing files in {directory}: {e}")
            return []
    
    def remove_file(self, path: str) -> bool:
        try:
            p = Path(path)
            if p.exists():
                p.unlink()
            return True
        except Exception as e:
            self.logger.error(f"Error removing file {path}: {e}")
            return False
