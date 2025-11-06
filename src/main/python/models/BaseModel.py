from python.duui.reqres import VideoDiarizationRequest
from python.duui.diarization import DiarizationResult
from .ModelType import ModelType

class BaseModel:

    testvar = 1

    model_id: str = "BaseModelId"

    model_version: str = "0.1"

    model_type: ModelType = ModelType.NONE

    def process(self, request: VideoDiarizationRequest) -> DiarizationResult: 
        raise NotImplementedError()