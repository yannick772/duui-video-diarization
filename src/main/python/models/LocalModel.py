from .BaseModel import BaseModel
from .ModelType import ModelType

class LocalModel(BaseModel):

    BaseModel.model_id = ""

    BaseModel.model_type = ModelType.LOCAL

    path: str = "path/to/local/model"
    

