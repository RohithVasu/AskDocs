import requests
from typing import Dict, Any
from app.core.settings import settings


def chat(question: str, collection_name: str) -> Dict[str, Any]:
    """Send a chat request to the backend."""
    try:
        payload = {"question": question, "collection_name": collection_name}
        
        response = requests.post(
            f"http://{settings.fastapi.host}:{settings.fastapi.port}/chat",
            json=payload
        )
        response.raise_for_status()
        
        # Return the response directly
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Chat request failed: {str(e)}")
        raise Exception(f"Failed to chat with documents: {str(e)}")