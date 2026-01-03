

import logging
import os
import torch
# from transformers import Wav2Vec2Processor, HubertForCTC

from ..duui.diarization import DiarizationResult
from ..duui.reqres import VideoDiarizationRequest
from .HuggingfaceModel import HuggingfaceModel
from .. import util

logger = logging.getLogger(__name__)

class HubertModel(HuggingfaceModel):
    
    HuggingfaceModel.model_id = "facebook/hubert-large-ls960-ft"

    # HuggingfaceModel.model_version = "06f233fe06e710322aca913c1bc4249a0d71fce1"

    HuggingfaceModel.model_dir = os.path.join(util.tmp_pth, "hubert")

    HuggingfaceModel.languages = ["en"]

    def preload(self):
        # self.model = HubertForCTC.from_pretrained(
        #     self.model_id
        # )

        # self.processor = Wav2Vec2Processor.from_pretrained(
        #     self.model_id
        # )
        pass

    def process(self, request: VideoDiarizationRequest) -> DiarizationResult:
        video_path = util.generate_video_from_base64(request.videoBase64, "test-video")
        audio_path = util.extract_audio_from_video(video_path)

        with open(audio_path, "rb") as audio_file:
            audio_bytes = audio_file.read() 

        try:
            input_values = self.processor(audio_bytes, return_tensors="pt").input_values
            result = self.model(
                input_values
            )
            logger.debug("result:")
            logger.debug(result)
        except Exception as ex:
            logger.exception(ex)

        logits = result.logits

        predicted_ids = torch.argmax(logits, dim=-1)

        logger.debug(predicted_ids)

        transcription = self.processor.decode(predicted_ids[0])

        diarization_result = self.__text_to_diarization_result(util.convert_object_to_json(transcription))

        return diarization_result
    
    def __text_to_diarization_result(self, text: str) -> DiarizationResult:
        result = DiarizationResult()
        with open(os.path.join(self.model_dir, "Response.json"), "w") as temp_json_file:
            temp_json_file.write(text)
        # TODO: add conversion process
        return result
        

# INSTANCE = HubertModel()
# INSTANCE.preload()