from typing import List, Dict
from pydantic import BaseModel

from .uima import UimaSentence, UimaVideo


class VideoDiarization(BaseModel):
    video: UimaVideo
    json: str

    # generated sentences based on the video data
    sentences: List[UimaSentence]
