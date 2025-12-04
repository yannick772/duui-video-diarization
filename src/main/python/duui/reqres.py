from typing import List, Optional
from pydantic import BaseModel

from .diarization import DiarizationResult

from .uima import DocumentModification


class VideoDiarizationRequest(BaseModel):
    videoBase64: str


class VideoDiarizationResponse(BaseModel):
    diarization: List[DiarizationResult] = []
    modification_meta: Optional[DocumentModification] = None