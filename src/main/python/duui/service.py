from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import BaseModel


# Settings
class Settings(BaseSettings):
    # Name of annotator
    duui_diarization_evaluation_annotator_name: str = "duui-diarization"

    # Version of annotator
    duui_diarization_evaluation_annotator_version: str = "unset"

    # Log level
    duui_diarization_evaluation_log_level: Optional[str] = "DEBUG"

    # Model LRU cache size
    duui_diarization_evaluation_model_cache_size: int = 1


# Capabilities
class DUUICapability(BaseModel):
    # List of supported languages by the annotator
    supported_languages: List[str]

    # Are results on same inputs reproducible without side effects?
    reproducible: bool


# Documentation response
class DUUIDocumentation(BaseModel):
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
    capability: DUUICapability

    # Analysis engine XML, if available
    implementation_specific: Optional[str]