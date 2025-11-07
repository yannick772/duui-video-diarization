FROM python:3.10.12

WORKDIR /usr/src/app

EXPOSE 9714

RUN DEBIAN_FRONTEND=noninteractive apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install ffmpeg -y

COPY ./requirements.txt ./requirements.txt
RUN pip install --no-deps -r requirements.txt

COPY ./src/main/python/diarization_evaluation.py ./src/main/python/diarization_evaluation.py
RUN python -u ./src/main/python/diarization_evaluation.py

COPY ./src/main/resources/TypeSystemDiarization.xml ./src/main/resources/TypeSystemDiarization.xml
COPY ./src/main/python/diarization_duui.py ./src/main/python/diarization_duui.py
COPY ./src/main/lua/duui_diarization.lua ./src/main/lua/duui_diarization.lua

ARG DUUI_DIARIZATION_EVALUATION_LOG_LEVEL="DEBUG"
ENV DUUI_DIARIZATION_EVALUATION_LOG_LEVEL=$DUUI_DIARIZATION_EVALUATION_LOG_LEVEL

ARG DUUI_DIARIZATION_EVALUATION_ANNOTATOR_NAME="duui-diarization"
ENV DUUI_DIARIZATION_EVALUATION_ANNOTATOR_NAME=$DUUI_DIARIZATION_EVALUATION_ANNOTATOR_NAME
ARG DUUI_DIARIZATION_EVALUATION_ANNOTATOR_VERSION="unset"
ENV DUUI_DIARIZATION_EVALUATION_ANNOTATOR_VERSION=$DUUI_DIARIZATION_EVALUATION_ANNOTATOR_VERSION

ENTRYPOINT ["uvicorn", "src.main.python.diarization_duui:app", "--host", "0.0.0.0", "--port" ,"9714"]
CMD ["--workers", "1"]