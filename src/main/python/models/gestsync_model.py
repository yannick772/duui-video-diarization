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

gestsync_pth = os.path.join(util.python_dir, "gestsync")
tmp_pth = os.path.join(util.tmp_pth, "GestSync")

class GestSyncModel(LocalModel):

    LocalModel.model_id = "Sindhu-Hegde/gestsync"
    LocalModel.model_version = "1.0"
    LocalModel.path = os.path.join(gestsync_pth, "checkpoints", "model_rgb.pth")
    LocalModel.languages = []

    def process(self, request: VideoDiarizationRequest) -> DiarizationResult:
        try:
            logger.debug("Starting GestSync process")
            processed_video = self.__process_video(request.videoBase64)
            logger.debug("GestSync video process finished")

            return processed_video

        except Exception as ex:
            logger.exception(ex)

    def __process_video(self, videoBase64: str) -> DiarizationResult:
        video_name = "test-video"
        video_pth = util.generate_video_from_base64(videoBase64, video_name, tmp_pth)
        lightasd_video_folder = os.path.dirname(video_pth)
        if (not os.path.exists(os.path.join(gestsync_pth, "preprocess", "inference_activespeaker.py"))):
            logger.warning("GestSync path was not found")
            return self.__json_to_diarizaiton_result("{}")
        cmd = f"python inference_activespeaker.py --checkpoint_path={self.path} --video_path={video_pth}"
        logger.debug("Processing Video")
        logger.debug("running command\n" + cmd + "\nas subprocess in directory\n" + gestsync_pth)
        retcode = subprocess.check_call(cmd, cwd=gestsync_pth)
        logger.debug("Video Processed under retcode: " + str(retcode))
        os.remove(video_pth)
        json_str = self.__visualization_json_format(video_name)
        return self.__json_to_diarizaiton_result(json_str)

    def __visualization_json_format(self, videoName: str) -> str:
        """
        Converts the ASD into a JSON string
        """
        path = os.path.join(tmp_pth, videoName, "temp", "pywork", "tracks.pckl")
        with open(path, "rb") as fil:
            tracks = pickle.load(fil)
        path = os.path.join(tmp_pth, videoName, "temp", "pywork", "scores.pckl")
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
    
# INSTANCE = GestSyncModel()