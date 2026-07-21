from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SearchRequest(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    query: str
    filters: dict | None = None
    limit: int = 20


class SearchResultItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    entity_type: str
    description: str | None = None


class SearchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    results: list[SearchResultItem]
    total: int
    query: str


class SavedSearchCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    query: str
    filters: dict | None = None


class SavedSearchRead(SavedSearchCreate):
    id: UUID


class SavedFilterCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    name: str
    entity_type: str
    filters: dict


class SavedFilterRead(SavedFilterCreate):
    id: UUID
