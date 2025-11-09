from contextlib import asynccontextmanager
import logging
from functools import lru_cache
from itertools import chain
from platform import python_version
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

from .models.HuggingfaceModel import HuggingfaceModel

from .models.TalkNetASD import TalkNetAsdModel
from .models.whisper import WhisperModel

from .duui.reqres import VideoDiarizationResponse, VideoDiarizationRequest
from .duui.service import Settings, DUUIDocumentation, DUUICapability
from .duui.uima import *
from .duui.diarization import DiarizationResult
from . import util

MODELS = {
    "TalkNetASD": TalkNetAsdModel(),
    "Whisper": WhisperModel()
}

settings = Settings()
supported_languages = sorted(list(set(chain(*[m.languages for m in MODELS.values()]))))
lru_cache_with_size = lru_cache(maxsize=settings.duui_diarization_evaluation_model_cache_size)
model_lock = Lock()

logging.basicConfig(level=settings.duui_diarization_evaluation_log_level)
logger = logging.getLogger(__name__)
logger.info("TTLab TextImager DUUI Transformers Sentiment")
logger.info("Name: %s", settings.duui_diarization_evaluation_annotator_name)
logger.info("Version: %s", settings.duui_diarization_evaluation_annotator_version)

device = 0 if torch.cuda.is_available() else -1
logger.info(f'USING {device}')

parent_dir = util.parent_dir
lightasd_pth = os.path.join(parent_dir, "Light-ASD-main")
resources_pth = util.resources_pth

typesystem_filename = os.path.join(resources_pth, "TypeSystemDiarization.xml")
logger.info("Loading typesystem from \"%s\"", typesystem_filename)
with open(typesystem_filename, 'rb') as f:
    typesystem = load_typesystem(f)
    logger.debug("Base typesystem:")
    logger.debug(typesystem.to_xml())

lua_communication_script_filename = os.path.join(parent_dir, "lua", "duui_diarization.lua")
logger.info("Loading Lua communication script from \"%s\"", lua_communication_script_filename)
with open(lua_communication_script_filename, 'rb') as f:
    lua_communication_script = f.read().decode("utf-8")
    logger.debug("Lua communication script:")
    logger.debug(lua_communication_script)

def startup():
    logger.debug("preloading models...")
    for m in MODELS.values(): 
        if isinstance(m, HuggingfaceModel):
            logger.debug("preloading model " + m.model_id)
            m.preload()
    logger.debug("finished preloading models")

app = FastAPI(
    openapi_url="/openapi.json",
    docs_url="/api",
    redoc_url=None,
    title=settings.duui_diarization_evaluation_annotator_name,
    description="DUUI Diarization Evaluation",
    version=settings.duui_diarization_evaluation_annotator_version,
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
    on_startup=[startup]
)

@app.get("/v1/communication_layer", response_class=PlainTextResponse)
def get_communication_layer() -> str:
    return lua_communication_script

@app.get("/v1/documentation")
def get_documentation() -> DUUIDocumentation:
    capabilities = DUUICapability(
        supported_languages=supported_languages,
        reproducible=True
    )

    documentation = DUUIDocumentation(
        annotator_name=settings.duui_diarization_evaluation_annotator_name,
        version=settings.duui_diarization_evaluation_annotator_version,
        implementation_lang="Python",
        meta={
            "python_version": python_version(),
            "python_version_full": sys_version,
            "transformers_version": transformers_version,
            "torch_version": torch.__version__,
        },
        docker_container_id="[TODO]",
        parameters={
            "model_name": MODELS.keys(),
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
def post_process(request: VideoDiarizationRequest) -> VideoDiarizationResponse:
    logger.debug("process detected")
    # logger.debug(request)
    modification_meta = None

    clean_cuda_cache()

    dt = datetime.now()

    modification_timestamp_seconds = int(time())

    response = VideoDiarizationResponse(
                diarization=None,
                meta=None,
                modification_meta=None
            )

    try:
        for model in MODELS.values():
            meta = AnnotationMeta(
                name=settings.duui_diarization_evaluation_annotator_name,
                version=settings.duui_diarization_evaluation_annotator_version,
                modelName=model.model_name,
                modelVersion=model.model_version,
            )
        
            logger.debug("using model: \'" + model.model_id + "\'")
            response = model.process(request)
            response.meta = meta
    except Exception as ex:
        logger.exception(ex)

    

    modification_meta_comment = f"{settings.duui_diarization_evaluation_annotator_name} ({settings.duui_diarization_evaluation_annotator_version})"
    modification_meta = DocumentModification(
        user="SpeakerDiarization",
        timestamp=modification_timestamp_seconds,
        comment=modification_meta_comment
    )

    response.modification_meta = modification_meta

    dte = datetime.now()
    print(dte, 'Finished processing', flush=True)
    print('Time elapsed', f'{dte-dt}', flush=True)

    clean_cuda_cache()

    return response

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

def fix_unicode_problems(text):
    # fix emoji in python string and prevent json error on response
    # File "/usr/local/lib/python3.8/site-packages/starlette/responses.py", line 190, in render
    # UnicodeEncodeError: 'utf-8' codec can't encode characters in position xx-yy: surrogates not allowed
    clean_text = text.encode('utf-16', 'surrogatepass').decode('utf-16', 'surrogateescape')
    return clean_text

