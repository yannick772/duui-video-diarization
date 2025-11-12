from typing import List, Optional
from pydantic import BaseModel

from .uima import AnnotationMeta

class UimaDiarizationToken(BaseModel):
    begin: int
    end: int
    timeStart: float
    timeEnd: float
    text: str
    speaker: int

class DiarizationResult(BaseModel):
    tokens: List[UimaDiarizationToken]
    meta: Optional[AnnotationMeta]
