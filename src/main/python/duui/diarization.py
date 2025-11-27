from typing import List, Optional
from pydantic import BaseModel

from .uima import AnnotationMeta

class UimaDiarizationToken(BaseModel):
    begin: int = 0
    end: int = 0
    timeStart: float = 0
    timeEnd: float = 0
    text: str = ""
    speaker: int = 0

class DiarizationResult(BaseModel):
    tokens: List[UimaDiarizationToken] = []
    meta: Optional[AnnotationMeta] = None
