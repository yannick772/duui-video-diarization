import math
from typing import List, Optional
from pydantic import BaseModel

from .uima import AnnotationMeta

class DiarizationEvaluation(BaseModel):
    speakers: int = 0
    avgLength: float = 0
    maxLength: int = 0
    minLength: int = math.inf
    speakerSwaps: int = 0


class UimaDiarizationToken(BaseModel):
    begin: int = 0
    end: int = 0
    timeStart: float = 0
    timeEnd: float = 0
    text: str = ""
    speaker: int = 0

class DiarizationResult(BaseModel):
    evaluation: DiarizationEvaluation = DiarizationEvaluation()
    tokens: List[UimaDiarizationToken] = []
    meta: Optional[AnnotationMeta] = None
