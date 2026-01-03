

import logging
import os
# import soundfile
# os.environ["TORCHAUDIO_BACKEND"] = "sox_io"

from speechbrain.inference.ASR import EncoderASR

from ..duui.diarization import DiarizationResult
from ..duui.reqres import VideoDiarizationRequest
from .HuggingfaceModel import HuggingfaceModel
from .. import util

logger = logging.getLogger(__name__)

class LibriSpeechModel(HuggingfaceModel):
    
    HuggingfaceModel.model_id = "speechbrain/asr-wav2vec2-librispeech"

    HuggingfaceModel.model_version = "ece5fabbf034c1073acae96d5401b25be96709d8"

    HuggingfaceModel.model_dir = os.path.join(util.tmp_pth, "librispeech")

    HuggingfaceModel.languages = ["en"]

    def preload(self):
        self.model = EncoderASR.from_hparams(
            source=self.model_id,
            savedir=self.model_dir,
            run_opts={"device":self.device}
        )

    def process(self, request: VideoDiarizationRequest) -> DiarizationResult:
        video_path = util.generate_video_from_base64(request.videoBase64, "test-video")
        audio_path = util.extract_audio_from_video(video_path)

        try:
            logger.debug(f"running LibriSpeech on file \'{audio_path}\'")
            result = self.model.transcribe_file(
                audio_path,
                use_torchaudio_streaming=True
            )
            logger.debug("result:")
            logger.debug(result)
        except Exception as ex:
            logger.exception(ex)
        
        diarization_result = self.__text_to_diarization_result(util.convert_object_to_json(result))

        os.environ.pop("TORCHAUDIO_BACKEND", None)

        return diarization_result
    
    def __text_to_diarization_result(self, text: str) -> DiarizationResult:
        result = DiarizationResult()
        with open(os.path.join(self.model_dir, "Response.json"), "w") as temp_json_file:
            temp_json_file.write(text)
        # TODO: add conversion process
        return result
        

# INSTANCE = LibriSpeechModel()
# INSTANCE.preload()