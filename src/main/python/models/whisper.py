import logging
import os
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from src.main.python.duui.reqres import VideoDiarizationRequest, VideoDiarizationResponse
from .HuggingfaceModel import HuggingfaceModel
from .. import util

logger = logging.getLogger(__name__)

INSTANCE = None

class WhisperModel(HuggingfaceModel):

    HuggingfaceModel.model_id = "openai/whisper-large-v3"

    HuggingfaceModel.model_version = "06f233fe06e710322aca913c1bc4249a0d71fce1"

    HuggingfaceModel.model_dir = os.path.join(util.tmp_pth, "whisper")

    HuggingfaceModel.model_name = "automatic-speech-recognition"

    HuggingfaceModel.languages = ["en"]

    def preload(self):
        model = AutoModelForSpeechSeq2Seq.from_pretrained(
            self.model_id,
            torch_dtype=self.torch_dtype,
            low_cpu_mem_usage=True,
            use_safetensors=True,
            cache_dir=self.model_dir,
        )
        model.to(self.device)

        processor = AutoProcessor.from_pretrained(self.model_id)

        self.pipe = pipeline(
            self.model_name,
            model=model,
            tokenizer=processor.tokenizer,
            revision=self.model_version,
            feature_extractor=processor.feature_extractor,
            return_timestamps=True,
            chunk_length_s=30,
            batch_size=16,
            torch_dtype=self.torch_dtype,
            device=self.device
        )

    def process(self, request: VideoDiarizationRequest):
        # dataset = load_dataset("distil-whisper/librispeech_long", "clean", split="validation")
        # sample = dataset[0]["audio"]

        video_path = util.generate_video_from_base64(request.videoBase64, "test-video")
        audio_path = util.extract_audio_from_video(video_path)

        try:
            result = self.pipe(audio_path)
            logger.debug("result:")
            logger.debug(result)
        except Exception as ex:
            logger.exception(ex)

        result_text = result["text"]
        
        response = VideoDiarizationResponse(
            json=result_text,
            meta=None,
            modification_meta=None
        )

        return response

if __name__ == "__main__":
    INSTANCE = WhisperModel()
    INSTANCE.preload()