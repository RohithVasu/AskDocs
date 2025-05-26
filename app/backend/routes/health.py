from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/health")
async def health_check():
    """
    Check if the server is running and healthy.
    Returns a 200 status code if the server is healthy.
    """
    return {"status": "healthy", "version": "0.0.1"}
