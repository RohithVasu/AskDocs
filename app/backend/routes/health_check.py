from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException

health_check_router = APIRouter()

@health_check_router.get("/health", tags=["health"])
async def health_check():
    """Check if the backend service is healthy and ready to serve requests."""
    try:
        # Add any specific health checks here
        return JSONResponse(content={"status": "healthy", "message": "Backend service is ready"})
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service health check failed: {str(e)}")
