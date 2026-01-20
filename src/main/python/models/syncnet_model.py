import json
import logging
import os
import pickle
import subprocess

import numpy
from scipy import signal
from ..duui.diarization import DiarizationResult, UimaDiarizationToken
from ..duui.reqres import VideoDiarizationRequest
from .. import util
from .LocalModel import LocalModel

logger = logging.getLogger(__name__)

syncnet_pth = os.path.join(util.parent_dir, "syncnet")
tmp_pth = os.path.join(util.tmp_pth, "syncnet")

class SyncNetModel(LocalModel):

    model_id = "joonson/syncnet_python"
    model_version = "1.0"
    path = os.path.join(util.resources_pth, "local_models", "syncnet", "syncnet_v2.model")
    languages = []

    def process(self, request: VideoDiarizationRequest) -> DiarizationResult:
        try:
            logger.debug("Starting SyncNet process")
            processed_video = self.__process_video(request.videoBase64)
            logger.debug("SyncNet video process finished")

            return processed_video

        except Exception as ex:
            logger.exception(ex)

    def __process_video(self, videoBase64: str) -> DiarizationResult:
        if (not os.path.exists(os.path.join(syncnet_pth, "run_pipeline.py"))):
            logger.error("SyncNet path \'" + syncnet_pth + "\' was not found")
            return self.__json_to_diarizaiton_result("{}")
        if (not os.path.exists(os.path.join(syncnet_pth, "run_syncnet.py"))):
            logger.error("SyncNet path \'" + syncnet_pth + "\' was not found")
            return self.__json_to_diarizaiton_result("{}")
        if (not os.path.exists(self.path)):
            logger.error("SyncNet model \'" + self.path + "\' not found")
            return self.__json_to_diarizaiton_result("{}")
        video_name = "test-video"
        video_pth = util.generate_video_from_base64(videoBase64, video_name)
        cmd = f"python run_pipeline.py --videofile {video_pth} --data_dir {tmp_pth}"
        logger.debug("Processing Video")
        logger.debug("running command\n" + cmd + "\nas subprocess in directory\n" + syncnet_pth)
        retcode = subprocess.check_call(cmd, cwd=syncnet_pth)
        cmd = f"python run_syncnet.py --videofile {video_pth} --data_dir {tmp_pth} --initial_model {self.path}"
        logger.debug("running command\n" + cmd + "\nas subprocess in directory\n" + syncnet_pth)
        retcode = subprocess.check_call(cmd, cwd=syncnet_pth)
        logger.debug("Video Processed under retcode: " + str(retcode))
        return self.__video_to_diarizaiton_result(video_name)

    def __visualization_json_format(self, videoName: str) -> list[list]:
        """
        Converts the ASD into a JSON string
        """
        path = os.path.join(tmp_pth, "pywork", "tracks.pckl")
        with open(path, "rb") as fil:
            tracks = pickle.load(fil)
        path = os.path.join(tmp_pth, "pywork", "activesd.pckl")
        with open(path, "rb") as fil:
            dists = pickle.load(fil)

        frames_dir = os.path.join(tmp_pth, "pyframes")
        frames_amount = len([name for name in os.listdir(frames_dir) if os.path.isfile(os.path.join(frames_dir, name))])
        logger.debug("found " + str(frames_amount) + " frames in pyframes")

        faces = [[] for _ in range(frames_amount)]

        for tidx, track in enumerate(tracks):
            mean_dists 	=  numpy.mean(numpy.stack(dists[tidx],1),1)
            minidx 		= numpy.argmin(mean_dists,0)
            
            fdist   	= numpy.stack([dist[minidx] for dist in dists[tidx]])
            fdist   	= numpy.pad(fdist, (3,3), 'constant', constant_values=10)

            fconf   = numpy.median(mean_dists) - fdist
            fconfm  = signal.medfilt(fconf,kernel_size=9)

            for fidx, frame in enumerate(track['track']['frame'].tolist()):
                faces[frame].append({'track': tidx, 'conf':fconfm[fidx], 's':track['proc_track']['s'][fidx], 'x':track['proc_track']['x'][fidx], 'y':track['proc_track']['y'][fidx]})

        logger.debug("frames with faces: " + str(len(faces)))
        return faces

    def __video_to_diarizaiton_result(self, video_name: str) -> DiarizationResult:
        result = DiarizationResult()
        obj = self.__visualization_json_format(video_name)

        for i, frame_faces in enumerate(obj):
            if (len(frame_faces) == 0):
                continue
            confidences = [face['conf'] for face in frame_faces]
            tracks = [face['track'] for face in frame_faces]
            speaker_index = max(range(len(confidences)), key=confidences.__getitem__)
            if (confidences[speaker_index] > 9):
                token = UimaDiarizationToken(
                    begin=i+1,
                    end=i+2,
                    speaker=tracks[speaker_index]
                )
                result.tokens.append(token)
        with open(os.path.join(tmp_pth, "Response.json"), "w") as temp_json_file:
            temp_json_file.write(util.convert_object_to_json(result))
        return result
    
# INSTANCE = SyncNetModel()