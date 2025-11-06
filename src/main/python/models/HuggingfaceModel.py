import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline

from .BaseModel import BaseModel
from .ModelType import ModelType

class HuggingfaceModel(BaseModel):

    BaseModel.model_id = "huggingface/model/name"

    BaseModel.model_version = "123456789"

    BaseModel.model_type = ModelType.HUGGINGFACE

    device = "cuda:0" if torch.cuda.is_available() else "cpu"
    torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

    model_dir = "path/to/cache/model"

    model_name = "model/name"

    def preload(self):
        raise NotImplementedError()
    
    def process(self):
        raise NotImplementedError()