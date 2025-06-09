import requests
from pathlib import Path
from typing import Dict, Any, Optional
from app.core.settings import settings
from loguru import logger

class APIService:
    def __init__(self):
        self.base_url = f"http://{settings.fastapi.host}:{settings.fastapi.port}"
        self.session = requests.Session()

    def check_health(self) -> bool:
        """Check if the backend service is healthy."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json().get("status") == "healthy"
        except requests.exceptions.RequestException as e:
            logger.error(f"Health check failed: {str(e)}")
            return False

    def upload_document(self, file: Path) -> Optional[str]:
        """Upload a document to the backend and return the collection name."""
        try:
            with open(file, "rb") as f:
                files = {"file": (file.name, f)}
                response = self.session.post(
                    f"{self.base_url}/upload",
                    files=files
                )
                response.raise_for_status()
                response_data = response.json()
                logger.info(f"Parsed response: {response_data}")
                return response_data.get("data", {}).get("collection_name", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to upload document: {str(e)}")
            raise Exception(f"Failed to upload document: {str(e)}")

    def chat(self, question: str, collection_name: str) -> Dict[str, Any]:
        """Send a chat request to the backend."""
        try:
            payload = {"question": question, "collection_name": collection_name}
            
            response = self.session.post(
                f"{self.base_url}/chat",
                json=payload
            )
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Chat request failed: {str(e)}")
            raise Exception(f"Failed to chat with documents: {str(e)}")
