from typing import TextIO
from datetime import datetime

class Logger:
    out: TextIO
    dev: bool
    
    def __init__(self, out: TextIO, dev: bool) -> None:
        self.out = out
        self.dev = dev

    def get_prefix(self):
        return f"[{datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')}]"
    
    def style(self, msg: str, color: int):
        if not self.dev:
            return msg
        
        return f"\033[{color}m{msg}\033[0m"

    def info(self, msg: str):
        self.out.write(f"[{self.style('INFO', 90)}]{self.get_prefix()} {msg}\n")

    def warn(self, msg: str):
        self.out.write(f"[{self.style('WARN', 93)}]{self.get_prefix()} {msg}\n")
        
    def error(self, msg: str):
        self.out.write(f"[{self.style('ERROR', 31)}]{self.get_prefix()} {msg}\n")