from typing import TextIO
from datetime import datetime

class Logger:
    out: TextIO
    
    def __init__(self, out: TextIO) -> None:
        self.out = out
    
    def get_prefix(self):
        return f"[{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}]"
    
    def info(self, msg: str):
        self.out.write(f"[INFO]{self.get_prefix()} {msg}\n")

    def warn(self, msg: str):
        self.out.write(f"[WARN]{self.get_prefix()} {msg}\n")
        
    def error(self, msg: str):
        self.out.write(f"[ERROR]{self.get_prefix()} {msg}\n")