import json
import logging
from functools import lru_cache
from itertools import chain
import pickle
from platform import python_version
import subprocess
import os
from sys import version as sys_version
from threading import Lock
from time import time
from typing import Dict, Union
from datetime import datetime

from cassis import load_typesystem
from fastapi import FastAPI, Response
from fastapi.responses import PlainTextResponse
import torch
from transformers import pipeline, __version__ as transformers_version, AutoTokenizer, AutoImageProcessor

from .duui.reqres import TextImagerResponse, TextImagerRequest
# from .duui.sentiment import SentimentSentence, SentimentSelection
from .duui.service import Settings, TextImagerDocumentation, TextImagerCapability
from .duui.uima import *
from .duui.diarization import VideoDiarization

SUPPORTED_MODELS = {
    # **CARDIFFNLP_TRBS,
    # **CARDIFFNLP_TRBSL,
    # **CARDIFFNLP_TXRBS,
    # **NLPTOWN_BBMUS,
    # **FINITEAUTOMATA_BBSA,
    # **SIEBERT_SRLE,
    # **JHARTMANN_SRLE3C,
    # **LIYUAN_ARSA,
    # **PHILSHMID_DBMCS2,
    # **CLAMPERT_MSC19,
    # **OLIVERGUHR_GSB,
    # **MDRAW_GNSB,
    # **CMARKEA_DBS,
}

settings = Settings()
supported_languages = sorted(list(set(chain(*[m["languages"] for m in SUPPORTED_MODELS.values()]))))
lru_cache_with_size = lru_cache(maxsize=settings.textimager_duui_transformers_sentiment_model_cache_size)
model_lock = Lock()

logging.basicConfig(level=settings.textimager_duui_transformers_sentiment_log_level)
logger = logging.getLogger(__name__)
logger.info("TTLab TextImager DUUI Transformers Sentiment")
logger.info("Name: %s", settings.textimager_duui_transformers_sentiment_annotator_name)
logger.info("Version: %s", settings.textimager_duui_transformers_sentiment_annotator_version)

device = 0 if torch.cuda.is_available() else -1
logger.info(f'USING {device}')

typesystem_filename = 'resources/TypeSystemDiarization.xml'
logger.info("Loading typesystem from \"%s\"", typesystem_filename)
with open(typesystem_filename, 'rb') as f:
    typesystem = load_typesystem(f)
    logger.debug("Base typesystem:")
    logger.debug(typesystem.to_xml())

lua_communication_script_filename = "lua/duui_diarization.lua"
logger.info("Loading Lua communication script from \"%s\"", lua_communication_script_filename)
with open(lua_communication_script_filename, 'rb') as f:
    lua_communication_script = f.read().decode("utf-8")
    logger.debug("Lua communication script:")
    logger.debug(lua_communication_script)

app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/api",
    redoc_url=None,
    title=settings.textimager_duui_transformers_sentiment_annotator_name,
    description="Transformers-based sentiment analysis for TTLab TextImager DUUI",
    version=settings.textimager_duui_transformers_sentiment_annotator_version,
    terms_of_service="https://www.texttechnologylab.org/legal_notice/",
    contact={
        "name": "TTLab Team",
        "url": "https://texttechnologylab.org",
        "email": "baumartz@stud.uni-frankfurt.de",
    },
    license_info={
        "name": "AGPL",
        "url": "http://www.gnu.org/licenses/agpl-3.0.en.html",
    },
)

@app.get("/v1/communication_layer", response_class=PlainTextResponse)
def get_communication_layer() -> str:
    return lua_communication_script

@app.get("/v1/documentation")
def get_documentation() -> TextImagerDocumentation:
    capabilities = TextImagerCapability(
        supported_languages=supported_languages,
        reproducible=True
    )

    documentation = TextImagerDocumentation(
        annotator_name=settings.textimager_duui_transformers_sentiment_annotator_name,
        version=settings.textimager_duui_transformers_sentiment_annotator_version,
        implementation_lang="Python",
        meta={
            "python_version": python_version(),
            "python_version_full": sys_version,
            "transformers_version": transformers_version,
            "torch_version": torch.__version__,
        },
        docker_container_id="[TODO]",
        parameters={
            "model_name": SUPPORTED_MODELS,
        },
        capability=capabilities,
        implementation_specific=None,
    )

    return documentation


@app.get("/v1/typesystem")
def get_typesystem() -> Response:
    xml = typesystem.to_xml()
    xml_content = xml.encode("utf-8")

    return Response(
        content=xml_content,
        media_type="application/xml"
    )


def clean_cuda_cache():
    if device >= 0:
        logger.info('emptying cuda cache')
        torch.cuda.empty_cache()
        logger.info('cuda cache empty')


@app.post("/v1/process")
def post_process(request: TextImagerRequest) -> TextImagerResponse:
    processed_selections = []
    meta = None
    modification_meta = None

    clean_cuda_cache()

    dt = datetime.now()

    try:
        modification_timestamp_seconds = int(time())

        logger.debug("Received:")
        logger.debug(request)

        if request.model_name not in SUPPORTED_MODELS:
            raise Exception(f"Model \"{request.model_name}\" is not supported!")

        if request.lang not in SUPPORTED_MODELS[request.model_name]["languages"]:
            raise Exception(f"Document language \"{request.lang}\" is not supported by model \"{request.model_name}\"!")

        logger.info("Using model: \"%s\"", request.model_name)
        model_data = SUPPORTED_MODELS[request.model_name]
        logger.debug(model_data)

        # processed_video = process_video(request.model_name, model_data, request.video)
        processed_video = process_video(request.video)

        
        processed_selections.append(
            VideoDiarization(
                # video = 
                # sentences = processed_sentences
            )
            # SentimentSelection(
            #     selection=selection.selection,
            #     sentences=processed_sentences
            # )
        )

        meta = UimaAnnotationMeta(
            name=settings.textimager_duui_transformers_sentiment_annotator_name,
            version=settings.textimager_duui_transformers_sentiment_annotator_version,
            modelName=request.model_name,
            modelVersion=model_data["version"],
        )

        modification_meta_comment = f"{settings.textimager_duui_transformers_sentiment_annotator_name} ({settings.textimager_duui_transformers_sentiment_annotator_version})"
        modification_meta = UimaDocumentModification(
            user="TextImager",
            timestamp=modification_timestamp_seconds,
            comment=modification_meta_comment
        )

    except Exception as ex:
        logger.exception(ex)

    #logger.debug(processed_selections)
    for ps in processed_selections:
        for s in ps.sentences:
            logger.debug(s)

    dte = datetime.now()
    print(dte, 'Finished processing', flush=True)
    print('Time elapsed', f'{dte-dt}', flush=True)

    clean_cuda_cache()

    return TextImagerResponse(
        selections=processed_selections,
        meta=meta,
        modification_meta=modification_meta
    )


@lru_cache_with_size
def load_model(model_name, model_version, labels_count, adapter_path=None):
    mo = model_name
    to = model_name

    # manually load model if:
    # model is local path, not on huggingface hub
    # or adapter is used
    if model_version is None or adapter_path is not None:
        if adapter_path is None:
            from transformers import AutoModelForSequenceClassification
            mo = AutoModelForSequenceClassification.from_pretrained(model_name, revision=model_version, local_files_only=True)
        else:
            from transformers import AutoAdapterModel
            mo = AutoAdapterModel.from_pretrained(model_name, revision=model_version, local_files_only=True)
            adapter_name = mo.load_adapter(adapter_path)
            mo.set_active_adapters(adapter_name)

        to = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        ip = AutoImageProcessor.from_pretrained(model_name, local_files_only=True)

    return pipeline(
        "video-diarization",
        model=mo,
        tokenizer=to,
        image_processor=ip,
        revision=model_version,
        top_k=labels_count,
        device=device
    )


def map_sentiment(sentiment_result: List[Dict[str, Union[str, float]]], sentiment_mapping: Dict[str, float], sentiment_polarity: Dict[str, List[str]], sentence: UimaSentence) -> VideoDiarization:
    # get label from top result and map to sentiment values -1, 0 or 1
    sentiment_value = 0.0
    top_result = sentiment_result[0]
    if top_result["label"] in sentiment_mapping:
        sentiment_value = sentiment_mapping[top_result["label"]]

    # get scores of all labels
    details = {
        s["label"]: s["score"]
        for s in sentiment_result
    }

    # calculate polarity: pos-neg
    polarities = {
        "pos": 0,
        "neu": 0,
        "neg": 0
    }
    for p in polarities:
        for l in sentiment_polarity[p]:
            for s in sentiment_result:
                if s["label"] == l:
                    polarities[p] += s["score"]

    polarity = polarities["pos"] - polarities["neg"]

    return VideoDiarization(
        sentence=sentence,
        sentiment=sentiment_value,
        score=top_result["score"],
        details=details,
        polarity=polarity,
        **polarities
    )


def fix_unicode_problems(text):
    # fix emoji in python string and prevent json error on response
    # File "/usr/local/lib/python3.8/site-packages/starlette/responses.py", line 190, in render
    # UnicodeEncodeError: 'utf-8' codec can't encode characters in position xx-yy: surrogates not allowed
    clean_text = text.encode('utf-16', 'surrogatepass').decode('utf-16', 'surrogateescape')
    return clean_text


def process_selection(model_name, model_data, selection, doc_len, batch_size, ignore_max_length_truncation_padding):
    for s in selection.sentences:
        s.text = fix_unicode_problems(s.text)

    texts = [
        model_data["preprocess"](s.text)
        for s in selection.sentences
    ]
    logger.debug("Preprocessed texts:")
    logger.debug(texts)

    with model_lock:
        model_type = "huggingface" if not "type" in model_data else model_data["type"]
        if model_type == "local":
            sentiment_analysis = load_model(model_data["path"], None, len(model_data["mapping"]))
        elif model_type == "adapter":
            adapter_model_type = "huggingface" if not "type" in model_data else model_data["type"]
            adapter_path = model_data["adapter_path"]
            if adapter_model_type == "local":
                sentiment_analysis = load_model(model_data["model_path"], None, len(model_data["mapping"]), adapter_path)
            else:
                sentiment_analysis = load_model(model_data["model_name"], model_data["model_version"], len(model_data["mapping"]), adapter_path)
        else:
            sentiment_analysis = load_model(model_name, model_data["version"], len(model_data["mapping"]))

        if ignore_max_length_truncation_padding:
            results = sentiment_analysis(
                texts, batch_size=batch_size
            )
        else:
            results = sentiment_analysis(
                texts, truncation=True, padding=True, max_length=model_data["max_length"], batch_size=batch_size
            )

    processed_sentences = [
        map_sentiment(r, model_data["mapping"], model_data["3sentiment"], s)
        for s, r
        in zip(selection.sentences, results)
    ]

    if len(results) > 1:
        begin = 0
        end = doc_len

        sentiments = 0
        for sentence in processed_sentences:
            sentiments += sentence.sentiment
        sentiment = sentiments / len(processed_sentences)

        scores = 0
        for sentence in processed_sentences:
            scores += sentence.score
        score = scores / len(processed_sentences)

        details = {}
        for sentence in processed_sentences:
            for d in sentence.details:
                if d not in details:
                    details[d] = 0
                details[d] += sentence.details[d]
        for d in details:
            details[d] = details[d] / len(processed_sentences)

        polaritys = 0
        for sentence in processed_sentences:
            polaritys += sentence.polarity
        polarity = polaritys / len(processed_sentences)

        poss = 0
        for sentence in processed_sentences:
            poss += sentence.pos
        pos = poss / len(processed_sentences)

        neus = 0
        for sentence in processed_sentences:
            neus += sentence.neu
        neu = neus / len(processed_sentences)

        negs = 0
        for sentence in processed_sentences:
            negs += sentence.neg
        neg = negs / len(processed_sentences)

        processed_sentences.append(
            VideoDiarization(
                sentence=UimaSentence(
                    text="",
                    begin=begin,
                    end=end,
                ),
                sentiment=sentiment,
                score=score,
                details=details,
                polarity=polarity,
                pos=pos,
                neu=neu,
                neg=neg
            )
        )

    return processed_sentences

# def process_video(model_name, model_data, video: UimaVideo):
    # diarization_pipeline = load_model(model_data["path"], None, len(model_data["mapping"]))
    # results = diarization_pipeline(
    #             video, truncation=True, padding=True, max_length=model_data["max_length"]
    #         )
    # cmd = "python demoTalkNet.py --videoName "+ video.name
    # subprocess.run(cmd)
    # visualization_json_format(video.name)


    # loading model
    # model_path = "pretrain_TalkSet.model"
    # if (not os.path.isfile(model_path)):
    #     link = "1AbN9fCf9IexMxEKXLQY2KYBlb-IhSEea"
    #     cmd = "gdown --id %s -O %s"%(link, model_path)
    #     subprocess.call(cmd, shell=True, stdout=None)
    # loadedState = torch.load(model_path, torch.device('cpu'))
    # for name, param in loadedState.items():
    #     origName = name
    #         if name not in selfState:
    #             name = name.replace("module.", "")
    #             if name not in selfState:
    #                 print("%s is not in the model."%origName)
    #                 continue
    #         if selfState[name].size() != loadedState[origName].size():
    #             sys.stderr.write("Wrong parameter length: %s, model: %s, loaded: %s"%(origName, selfState[name].size(), loadedState[origName].size()))
    #             continue
    #         selfState[name].copy_(param)

def process_video(video: UimaVideo):
    cmd = "python demoTalkNet.py --videoName "+ video.name
    subprocess.run(cmd)
    visualization_json_format(video.name)

# def load_model():
#     model_path = "pretrain_TalkSet.model"
#     if (not os.path.isfile(model_path)):
#         link = "1AbN9fCf9IexMxEKXLQY2KYBlb-IhSEea"
#         cmd = "gdown --id %s -O %s"%(link, model_path)
#         subprocess.call(cmd, shell=True, stdout=None)
#     loadedState = torch.load(model_path)
#     for name, param in loadedState.items():

def visualization_json_format(videoName: str, modelPath: str = "src\main\Light-ASD-main"):
    """
    Converts the ASD into a JSON string
    """
    path = os.path.join(modelPath, "demo/" + videoName + "/pywork", "tracks.pckl")
    fil = open(path, "rb")
    tracks = pickle.load(fil)
    path = os.path.join(modelPath, "demo/" + videoName + "/pywork", "scores.pckl")
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