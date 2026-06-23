from enum import Enum

class Type(str, Enum):
    SystemEvaluation = "SystemEvaluation",
    DataEvaluation = "DataEvaluation",
    HumanEvaluation = "HumanEvaluation",
    EcologicalEvaluation = "EcologicalEvaluation",

