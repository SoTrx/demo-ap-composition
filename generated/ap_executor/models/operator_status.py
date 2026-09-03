from enum import Enum

class OperatorStatus(str, Enum):
    Pending = "pending",
    Running = "running",
    Success = "success",
    Error = "error",
    Skipped = "skipped",

