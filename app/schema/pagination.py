from pydantic import BaseModel, Field
from typing import Optional


class PaginationResponse(BaseModel):
    total_records: int | None
    current_page: int | None
    total_pages: int | None
    next_page: int | None
    prev_page: int | None


class PaginationRequest(BaseModel):
    page: int = Field(1, ge=1)
    limit: int = Field(5, ge=1)

    class Config:
        # Allow alias usage for request query parameters
        populate_by_name = True
    


