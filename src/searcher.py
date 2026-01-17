"""File searcher module."""
import mmap
import os
from typing import Optional, Set


class FileSearcher:
    """Handles file searching with caching."""
    
    def __init__(self, filepath: str, reread_on_query: bool = False):
        """Initialize searcher."""
        if not os.path.isfile(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        self.filepath = filepath
        self.reread_on_query = reread_on_query
        self.lines_set: Optional[Set[bytes]] = None
        
        if not reread_on_query:
            self._load()
    
    def _load(self) -> None:
        """Load file into memory for fast search."""
        with open(self.filepath, 'rb') as f:
            mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            self.lines_set = set()
            for line in iter(mm.readline, b""):
                self.lines_set.add(line.rstrip(b'\r\n'))
            mm.close()
    
    def exists(self, query: str) -> bool:
        """Check if exact string exists in file."""
        q_bytes = query.encode('utf-8')
        
        if self.reread_on_query:
            self._load()
        
        return q_bytes in self.lines_set