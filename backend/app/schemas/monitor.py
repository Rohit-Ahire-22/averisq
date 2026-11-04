from pydantic import BaseModel, HttpUrl, Field, ConfigDict
from uuid import UUID
class MonitorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    url: HttpUrl
    interval: int = Field(ge=10, le=3600)

class MonitorResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    url: HttpUrl
    interval: int
    status: str

class MonitorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    url: HttpUrl | None = None
    interval: int | None = Field(default=None, ge=10, le=3600)

class MonitorListResponse(BaseModel):
    items: list[MonitorResponse]
    total: int
    limit: int
    offset: int
