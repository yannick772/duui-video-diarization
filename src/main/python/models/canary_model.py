

import logging
import os
# from nemo.collections.asr.models import EncDecMultiTaskModel

from ..duui.diarization import DiarizationResult
from ..duui.reqres import VideoDiarizationRequest
from .HuggingfaceModel import HuggingfaceModel
from .. import util

logger = logging.getLogger(__name__)

class CanaryModel(HuggingfaceModel):
    
    HuggingfaceModel.model_id = "nvidia/canary-1b"

    # HuggingfaceModel.model_version = "06f233fe06e710322aca913c1bc4249a0d71fce1"

    HuggingfaceModel.model_dir = os.path.join(util.tmp_pth, "canary")

    HuggingfaceModel.languages = ["en"]

    def preload(self):
        # self.model = EncDecMultiTaskModel.from_pretrained(
        #     self.model_id
        # )
        pass

    def process(self, request: VideoDiarizationRequest) -> DiarizationResult:
        video_path = util.generate_video_from_base64(request.videoBase64, "test-video")
        audio_path = util.extract_audio_from_video(video_path)

        input_manifest_file_path = os.path.join(self.model_dir, "input_manifest.json")

        with open(input_manifest_file_path, "w") as input_manifest_file:
            input_manifest_file.write(
                "\{"+
                f"\"audio_filepath\": \"{audio_path}\"" +
                f"\"duration\": \"None\"" +
                f"\"taskname\": \"asr\"" +
                f"\"source_lang\": \"{self.languages[0]}\"" +
                f"\"target_lang\": \"{self.languages[0]}\"" +
                f"\"pnc\": \"yes\"" +
                f"\"answer\": \"na\"" +
                "\}"
            )

        try:
            result = self.model.transcribe(
                input_manifest_file_path,
                batch_size=16
            )
            logger.debug("result:")
            logger.debug(result)
        except Exception as ex:
            logger.exception(ex)

        result_text = result[0].text

        logger.debug(result_text)
        
        diarization_result = self.__text_to_diarization_result(util.convert_object_to_json(result))

        return diarization_result
    
    def __text_to_diarization_result(self, text: str) -> DiarizationResult:
        result = DiarizationResult()
        with open(os.path.join(self.model_dir, "Response.json"), "w") as temp_json_file:
            temp_json_file.write(text)
        # TODO: add conversion process
        return result
        

# INSTANCE = CanaryModel()
# INSTANCE.preload()