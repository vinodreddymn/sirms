from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.search import SearchResponse

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
async def global_search(query: str = Query(...), db: AsyncSession = Depends(get_db)) -> SearchResponse:
    return SearchResponse(results=[], total=0, query=query)
