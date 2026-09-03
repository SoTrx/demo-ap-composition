from enum import Enum

class ExecutionStatus(str, Enum):
    Pending = "pending",
    Running = "running",
    Success = "success",
    Partial_success = "partial_success",
    Error = "error",

