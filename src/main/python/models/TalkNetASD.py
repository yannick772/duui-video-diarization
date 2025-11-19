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

lightasd_pth = os.path.join(util.parent_dir, "Light-ASD-main")
tmp_pth = os.path.join(util.tmp_pth, "LightTalkASD")

class TalkNetAsdModel(LocalModel):

    LocalModel.model_id = "TaoRuijie/TalkNet-ASD/pretrain_TalkSet"
    LocalModel.model_version = "1.0"
    LocalModel.path = "models/TaoRuijie/TalkNet-ASD/pretrain_TalkSet.model"
    LocalModel.languages = []

    def process(self, request: VideoDiarizationRequest):
        try:
            processed_video = self.__process_video(request.videoBase64)
            logger.debug("processed video json:")
            logger.debug(processed_video)

            return processed_video

        except Exception as ex:
            logger.exception(ex)

    def __process_video(self, videoBase64: str):
        video_name = "test-video"
        video_pth = util.generate_video_from_base64(videoBase64, video_name)
        cmd = "python Columbia_test.py --videoName "+ video_name + " --videoFolder " + os.path.dirname(video_pth)
        logger.debug("Processing Video")
        retcode = subprocess.check_call(cmd, cwd=lightasd_pth)
        logger.debug("Video Processed under retcode: " + str(retcode))
        json_str = self.__visualization_json_format(video_name)
        return self.__json_to_diarizaiton_result(json_str)

    def __visualization_json_format(self, videoName: str, videoPath: str = "resources"):
        """
        Converts the ASD into a JSON string
        """
        path = os.path.join(tmp_pth, videoName, "pywork", "tracks.pckl")
        fil = open(path, "rb")
        tracks = pickle.load(fil)
        path = os.path.join(tmp_pth, videoName, "pywork", "scores.pckl")
        fil = open(path, "rb")
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
    
    def __json_to_diarizaiton_result(json_str: str):
        result =  DiarizationResult()
        x = util.convert_json_to_object(json_str)
        for item in x:
            token = UimaDiarizationToken()
            token.begin = item["frame_number"]
            token.speaker = filter(item["faces"], lambda d: bool(d["speaking"]))[0]["face_id"]
            result.tokens.append(token)
        
        return result
    
INSTANCE = TalkNetAsdModel()