SUPPORTED_MODEL = {
    "TaoRuijie/TalkNet-ASD/pretrain_TalkSet": {
        "version": "1.0",
        "type":  "local",
        "path": "models/TaoRuijie/TalkNet-ASD/pretrain_TalkSet.model",
        "preprocess": lambda video: video,
        "languages": ["en"]
    }
}

if __name__ == '__main__':
    pass