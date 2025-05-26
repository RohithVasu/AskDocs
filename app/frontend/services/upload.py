import requests
from pathlib import Path
from app.core.settings import settings
from loguru import logger

def upload_document(file: Path) -> str:
    """Upload a document to the backend and return the collection name."""
    try:
        with open(file, "rb") as f:
            files = {"file": (file.name, f)}
            response = requests.post(
                f"http://{settings.fastapi.host}:{settings.fastapi.port}/upload",
                files=files
            )
            response_data = response.json()
            logger.info(f"Parsed response: {response_data}")
            return response_data.get("data", {}).get("collection_name", "")
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to upload document: {str(e)}")
        raise Exception(f"Failed to upload document: {str(e)}")