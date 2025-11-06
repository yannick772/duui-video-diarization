from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from .diarization import DiarizationResult

from .uima import DocumentModification


class VideoDiarizationRequest(BaseModel):
    model_config = ConfigDict()
    model_config['protected_namespaces'] = ()

    # video: UimaVideo
    videoBase64: str
    # lang: str
    # video_len: int
    # model_name: str
    # batch_size: int
    # ignore_max_length_truncation_padding: bool


class VideoDiarizationResponse(BaseModel):
    diarization: List[DiarizationResult]
    modification_meta: Optional[DocumentModification]