import base64
import json
import os
import logging
import subprocess
from types import SimpleNamespace
from typing import List

from .duui.diarization import DiarizationResult, UimaDiarizationToken 

logger = logging.getLogger(__name__)

parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
resources_pth = os.path.join(parent_dir, "resources")
tmp_pth = os.path.join(resources_pth, "tmp")

def generate_video_from_base64(encodedStr: str, name: str, path: str = ""):
    logger.debug("converting video from base64 string...")
    video_file_pth = path if len(path) > 0 else tmp_pth
    if (not os.path.exists(path)):
        os.makedirs(path)
    video_file_pth = os.path.join(video_file_pth, name + ".mp4")
    # video_file = open(video_file_pth, "wb")
    with open(video_file_pth, "wb") as video_file:
        video_file.write(base64.b64decode(encodedStr))
    logger.debug("video generated")
    return video_file_pth

def extract_audio_from_video(video_pth: str):
    dir_pth = os.path.dirname(video_pth)
    video_name = os.path.basename(video_pth).split(".")[0]
    audio_pth = os.path.join(dir_pth, video_name + "-audio.wav")
    cmd = [
        "ffmpeg",
        "-i",
        video_pth,
        "-ab",
        "160k",
        "-ac",
        "2",
        "-ar",
        "44100",
        "-vn",
        audio_pth
    ]
    retcode = subprocess.check_call(cmd)
    logger.debug("finished command under retcode: " + str(retcode))
    return audio_pth

def clear_temp_folder():
    for dir in os.walk(tmp_pth, topdown=False):
        if os.path.isfile():
            os.remove(dir)
        if os.path.isdir(dir):
            os.rmdir(dir)

def convert_json_to_object(json_str: str) -> List[SimpleNamespace]:
    x = json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))
    return x

def convert_object_to_json(object) -> str:
    json_str = json.dumps(object, default=lambda d: d.__dict__)
    return json_str

def compress_diarization_result_tokens(diarization_result: DiarizationResult) -> DiarizationResult:
    compressed_diarization_result = DiarizationResult()
    if len(diarization_result.tokens) > 0:
        compressed_diarization_result.tokens.append(diarization_result.tokens.pop(0))
        for token in diarization_result.tokens:
            last_token = compressed_diarization_result.tokens.pop()
            if token.speaker == last_token.speaker:
                last_token.end = token.end
                compressed_diarization_result.tokens.append(last_token)
            else:
                compressed_diarization_result.tokens.append(last_token)
                compressed_diarization_result.tokens.append(token)
    compressed_diarization_result.meta = diarization_result.meta
    return compressed_diarization_result