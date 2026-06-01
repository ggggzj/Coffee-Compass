from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(..., alias="DATABASE_URL")
    google_places_api_key: str = Field(..., alias="GOOGLE_PLACES_API_KEY")
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")

    usc_lat: float = Field(34.0224, alias="USC_LAT")
    usc_lng: float = Field(-118.2851, alias="USC_LNG")
    ingest_radius_meters: int = Field(5000, alias="INGEST_RADIUS_METERS")
    ingest_limit: int = Field(100, alias="INGEST_LIMIT")

    slot_extractor_model: str = Field("gpt-4o-mini", alias="SLOT_EXTRACTOR_MODEL")
    review_tagger_model: str = Field("gpt-4o-mini", alias="REVIEW_TAGGER_MODEL")
    embedding_model: str = Field("text-embedding-3-small", alias="EMBEDDING_MODEL")
    review_tagger_impl: str = Field("v1", alias="REVIEW_TAGGER_IMPL")


def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
