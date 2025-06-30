from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from .diarization import VideoDiarization

# from .sentiment import SentimentSelection
from .uima import UimaSentenceSelection, UimaAnnotationMeta, UimaDocumentModification, UimaVideo


class TextImagerRequest(BaseModel):
    model_config = ConfigDict(str_max_length=10)
    model_config['protected_namespaces'] = ()

    video: UimaVideo
    lang: str
    video_len: int
    model_name: str
    batch_size: int
    # ignore_max_length_truncation_padding: bool


class TextImagerResponse(BaseModel):
    diarization: VideoDiarization
    meta: Optional[UimaAnnotationMeta]
    modification_meta: Optional[UimaDocumentModification]