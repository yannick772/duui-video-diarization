from enum import Enum

class ModelType(Enum):
    LOCAL = "local",
    HUGGINGFACE = "huggingface",
    NONE = "none"