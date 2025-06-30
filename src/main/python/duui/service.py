from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import BaseModel


# Settings
class Settings(BaseSettings):
    # Name of annotator
    textimager_duui_transformers_sentiment_annotator_name: str = "My API"

    # Version of annotator
    textimager_duui_transformers_sentiment_annotator_version: str = "2.1.0"

    # Log level
    textimager_duui_transformers_sentiment_log_level: Optional[str] = None

    # Model LRU cache size
    textimager_duui_transformers_sentiment_model_cache_size: int = 0


# Capabilities
class TextImagerCapability(BaseModel):
    # List of supported languages by the annotator
    supported_languages: List[str]

    # Are results on same inputs reproducible without side effects?
    reproducible: bool


# Documentation response
class TextImagerDocumentation(BaseModel):
    # Name of this annotator
    annotator_name: str

    # Version of this annotator
    version: str

    # Annotator implementation language (Python, Java, ...)
    implementation_lang: Optional[str]

    # Optional map of additional meta data
    meta: Optional[dict]

    # Docker container id, if any
    docker_container_id: Optional[str]

    # Optional map of supported parameters
    parameters: Optional[dict]

    # Capabilities of this annotator
    capability: TextImagerCapability

    # Analysis engine XML, if available
    implementation_specific: Optional[str]