import json
import logging
import os
import pickle
import subprocess
from ..duui.diarization import DiarizationResult, UimaDiarizationToken
from ..duui.reqres import VideoDiarizationRequest
from .. import util
from .LocalModel import LocalModel

logger = logging.getLogger(__name__)

loconet_pth = os.path.join(util.python_dir, "LoCoNet_ASD")
tmp_pth = os.path.join(util.tmp_pth, "LoCoNet")

class LoCoNetModel(LocalModel):

    LocalModel.model_id = "SJTUwxz/LoCoNet_ASD"
    LocalModel.model_version = "1.0"
    LocalModel.path = os.path.join(loconet_pth, "model", "loconet_ava_best.model")
    LocalModel.languages = []

    def process(self, request: VideoDiarizationRequest) -> DiarizationResult:
        try:
            logger.debug("Starting LoCoNet process")
            processed_video = self.__process_video(request.videoBase64)
            logger.debug("LoCoNet video process finished")

            return processed_video

        except Exception as ex:
            logger.exception(ex)

    def __process_video(self, videoBase64: str) -> DiarizationResult:
        video_name = "test-video"
        video_pth = util.generate_video_from_base64(videoBase64, video_name, os.path.join(tmp_pth, "clips_video"))
        if (not os.path.exists(os.path.join(loconet_pth, "test_multicard.py"))):
            logger.warning("LoCoNet path was not found")
            os.remove(video_pth)
            return self.__json_to_diarizaiton_result("{}")
        config_pth = self.__print_config(video_pth)
        cmd = f"python -W ignore::UserWarning test_multicard.py --cfg {config_pth}"
        logger.debug("Processing Video")
        logger.debug("running command\n" + cmd + "\nas subprocess in directory\n" + loconet_pth)
        retcode = subprocess.check_call(cmd, cwd=loconet_pth)
        logger.debug("Video Processed under retcode: " + str(retcode))
        os.remove(video_pth)
        json_str = self.__visualization_json_format(video_name)
        return self.__json_to_diarizaiton_result(json_str)

    def __visualization_json_format(self, videoName: str) -> str:
        """
        Converts the ASD into a JSON string
        """
        path = os.path.join(tmp_pth, videoName, "pywork", "tracks.pckl")
        with open(path, "rb") as fil:
            tracks = pickle.load(fil)
        path = os.path.join(tmp_pth, videoName, "pywork", "scores.pckl")
        with open(path, "rb") as fil:
            scores = pickle.load(fil)

        # video = cv2.VideoCapture("data/" + videoName + "/pyavi/video.avi")
        # video_width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        # video_height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        # video.release()

        # Convert face tracks and scores to the desired JSON format
        output_data = []
        for track_idx, track in enumerate(tracks):
            # Get the frame numbers for the current track
            frames = track["track"]["frame"]

            # Get the bounding box information for the current track
            boxes = track["proc_track"]

            # Get the speaking scores for the current track
            # If the track index is out of range, use an empty list
            speaking_scores = scores[track_idx] if track_idx < len(scores) else []

            for i, frame in enumerate(frames):
                # Check if the current index is within the valid range of the bounding box information
                # If not, break the loop and move to the next track
                if i >= len(boxes["x"]) or i >= len(boxes["y"]) or i >= len(boxes["s"]):
                    break

                # Calculate bounding box coordinates
                x0 = int(boxes["x"][i] - boxes["s"][i])
                y0 = int(boxes["y"][i] - boxes["s"][i])
                x1 = int(boxes["x"][i] + boxes["s"][i])
                y1 = int(boxes["y"][i] + boxes["s"][i])

                # Determine speaking status
                speaking = (
                    bool(speaking_scores[i] >= 0) if i < len(speaking_scores) else False
                )

                # Create the bounding box dictionary
                box = {
                    "face_id": track_idx,
                    "x0": x0,
                    "y0": y0,
                    "x1": x1,
                    "y1": y1,
                    "speaking": speaking,
                }

                # Create a dictionary for each frame if it doesn't exist
                frame_data = next(
                    (
                        data
                        for data in output_data
                        if data["frame_number"] == int(frame)
                    ),
                    None,
                )
                if frame_data is None:
                    frame_data = {"frame_number": int(frame), "faces": []}
                    output_data.append(frame_data)

                # Add the current face's bounding box and speaking status to the frame's data
                frame_data["faces"].append(box)

        # Convert the output data to JSON string
        json_str = json.dumps(output_data)
        # Save json file
        return json_str

    def __json_to_diarizaiton_result(self, json_str: str) -> DiarizationResult:
        result =  DiarizationResult()
        x = util.convert_json_to_object(json_str)
        for frame in x:
            frame_speakers = list(filter(lambda d: bool(d.speaking), frame.faces))
            for frame_speaker in frame_speakers:
                token = UimaDiarizationToken(
                    begin=frame.frame_number,
                    end=frame.frame_number + 1,
                    speaker=frame_speaker.face_id
                )
                result.tokens.append(token)
        with open(os.path.join(tmp_pth, "Response.json"), "w") as result_file:
            result_file.write(util.convert_object_to_json(result))
        return result
    
    def __print_config(self, video_path: str):
        if (not os.path.exists(os.path.join(loconet_pth, "configs"))):
            logger.warning("LoCoNet Config directory was not found")
            return
        config_path = os.path.join(loconet_pth, "configs", "diarization.yaml")
        config_content = f"""
SEED: "20210617"
NUM_GPUS: 4
NUM_WORKERS: 6
LOG_NAME: 'config.txt'
OUTPUT_DIR: '{tmp_pth}'  # savePath
evalDataType: "val"
downloadAVA: False
evaluation: False
RESUME: False
RESUME_PATH: '{self.path}'
RESUME_EPOCH: 0

DATA:
    dataPathAVA: '{os.path.dirname(video_path)}'

DATALOADER:
    nDataLoaderThread: 4
    

SOLVER:
    OPTIMIZER: "adam"
    BASE_LR: 5e-5
    SCHEDULER:
        NAME: "multistep"
        GAMMA: 0.95

MODEL:
    NUM_SPEAKERS: 3
    CLIP_LENGTH: 200
    AV: "speaker_temporal"
    AV_layers: 3
    ADJUST_ATTENTION: 0

TRAIN:
    BATCH_SIZE: 1
    MAX_EPOCH: 25
    AUDIO_AUG: 1 
    TEST_INTERVAL: 1
    TRAINER_GPU: 4


VAL:
    BATCH_SIZE: 1

TEST:
    BATCH_SIZE: 1
    DATASET: 'seen'
    MODEL: 'unseen'
                """
        with open(config_path, "w") as config_file:
            config_file.write(config_content)
        return config_path
            
    
# INSTANCE = LoCoNetModel()