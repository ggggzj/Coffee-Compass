from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(5, ge=1, le=20)


class ParsedFilters(BaseModel):
    has_outlet: bool | None
    open_now: bool | None
    price_max: int | None


class ParsedQuerySchema(BaseModel):
    semantic_query: str
    filters: ParsedFilters


class SearchResult(BaseModel):
    id: int
    name: str
    address: str
    lat: float
    lng: float
    rating: float | None
    price_level: int | None
    has_outlet: bool | None
    has_wifi: bool | None
    noise_level: str | None
    good_for_studying: bool | None
    open_now: bool
    similarity: float
    ambience_text: str


class SearchResponse(BaseModel):
    parsed: ParsedQuerySchema
    results: list[SearchResult]


class AgentChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    user_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class RecommendedCafe(BaseModel):
    id: int
    name: str
    lat: float
    lng: float
    price_level: int | None = None
    has_outlet: bool | None = None
    noise_level: str | None = None
    ambience_text: str | None = None
    open_now: bool | None = None
