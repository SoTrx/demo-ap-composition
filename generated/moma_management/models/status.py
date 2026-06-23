from enum import Enum

class Status(str, Enum):
    Ready = "ready",
    Loaded = "loaded",
    Staged = "staged",

