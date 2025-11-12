FROM python:3.10.12

WORKDIR /usr/src/app

EXPOSE 9714

RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install ffmpeg -y

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-deps --default-timeout=100 -r requirements.txt

# copy util
COPY ./src/main/python/__init__.py ./src/main/python/__init__.py
COPY ./src/main/python/util.py ./src/main/python/util.py

# copy duui classes
COPY ./src/main/python/duui/__init__.py ./src/main/python/duui/__init__.py
COPY ./src/main/python/duui/diarization.py ./src/main/python/duui/diarization.py
COPY ./src/main/python/duui/reqres.py ./src/main/python/duui/reqres.py
COPY ./src/main/python/duui/service.py ./src/main/python/duui/service.py
COPY ./src/main/python/duui/uima.py ./src/main/python/duui/uima.py

# copy model subclasses
COPY ./src/main/python/models/__init__.py ./src/main/python/models/__init__.py
COPY ./src/main/python/models/ModelType.py ./src/main/python/models/ModelType.py
COPY ./src/main/python/models/BaseModel.py ./src/main/python/models/BaseModel.py
COPY ./src/main/python/models/LocalModel.py ./src/main/python/models/LocalModel.py
COPY ./src/main/python/models/HuggingfaceModel.py ./src/main/python/models/HuggingfaceModel.py

# copy model classes
COPY ./src/main/Light-ASD-main ./src/main/Light-ASD-main
COPY ./src/main/python/models/TalkNetASD.py ./src/main/python/models/TalkNetASD.py
# CMD ["python", "-m", "./src/main/python/models/TalkNetASD.py"]
RUN python -m src.main.python.models.TalkNetASD
COPY ./src/main/python/models/whisper.py ./src/main/python/models/whisper.py
# CMD ["python", "-m", "./src/main/python/models/whisper.py"]
RUN python -m src.main.python.models.whisper

COPY ./src/main/resources/TypeSystemDiarization.xml ./src/main/resources/TypeSystemDiarization.xml
COPY ./src/main/python/diarization_duui.py ./src/main/python/diarization_duui.py
COPY ./src/main/lua/duui_diarization.lua ./src/main/lua/duui_diarization.lua

ARG DUUI_DIARIZATION_EVALUATION_LOG_LEVEL="DEBUG"
ENV DUUI_DIARIZATION_EVALUATION_LOG_LEVEL=$DUUI_DIARIZATION_EVALUATION_LOG_LEVEL

ARG DUUI_DIARIZATION_EVALUATION_ANNOTATOR_NAME="duui-diarization"
ENV DUUI_DIARIZATION_EVALUATION_ANNOTATOR_NAME=$DUUI_DIARIZATION_EVALUATION_ANNOTATOR_NAME
ARG DUUI_DIARIZATION_EVALUATION_ANNOTATOR_VERSION="unset"
ENV DUUI_DIARIZATION_EVALUATION_ANNOTATOR_VERSION=$DUUI_DIARIZATION_EVALUATION_ANNOTATOR_VERSION
ARG DUUI_DIARIZATION_EVALUATION_MODEL_CACHE_SIZE=1
ENV DUUI_DIARIZATION_EVALUATION_MODEL_CACHE_SIZE=$DUUI_DIARIZATION_EVALUATION_MODEL_CACHE_SIZE

ENTRYPOINT ["uvicorn", "src.main.python.diarization_duui:app", "--host", "0.0.0.0", "--port" ,"9714"]
CMD ["--workers", "1"]