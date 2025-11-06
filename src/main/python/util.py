import base64
import json
import os
import logging
import subprocess
from types import SimpleNamespace 

logger = logging.getLogger(__name__)

parent_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
resources_pth = os.path.join(parent_dir, "resources")
tmp_pth = os.path.join(resources_pth, "tmp")

def generate_video_from_base64(encodedStr: str, name: str):
    logger.debug("converting video from base64 string...")
    video_file_pth = os.path.join(tmp_pth, name + ".mp4")
    video_file = open(video_file_pth, "wb")
    video_file.write(base64.b64decode(encodedStr))
    video_file.close()
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

def convert_json_to_object(json_str: str):
    x = json.loads(x, object_hook=lambda d: SimpleNamespace(**d))
    return x
