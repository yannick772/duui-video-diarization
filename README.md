# duui-video-diarization
Pipeline for DUUI for diarization using video-audio information

Create the Docker Image by running the following command from the project folder:
```
docker build -t duui/diarization-evaluation -f ./src/main/docker/Dockerfile .
```

Alternatively you can run the server manually by creating a conda enviornment and running the commands
```
pip install --no-deps --default-timeout=100 -r requirements.txt
```
```
uvicorn src.main.python.diarization_duui:app --host 0.0.0.0 --port 8000
```