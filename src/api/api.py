from fastapi import APIRouter

from src.api.endpoints import example_route

router = APIRouter()


@router.get("/health")
async def root():
    return {"message": "I'm alive!"}


router.include_router(**example_route)
