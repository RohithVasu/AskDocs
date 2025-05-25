import requests
from typing import Dict, Any
from pathlib import Path
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Get backend URL from environment or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

class APIService:
    @staticmethod
    def upload_document(file: Path) -> Dict[str, Any]:
        """Upload a document to the backend."""
        try:
            with open(file, "rb") as f:
                files = {"file": (file.name, f)}
                response = requests.post(f"{BACKEND_URL}/upload", files=files)
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to upload document: {str(e)}")

    @staticmethod
    def chat_with_documents(question: str, chat_history: list = None) -> Dict[str, Any]:
        """Send a chat request to the backend."""
        try:
            payload = {"question": question}
            if chat_history:
                payload["chat_history"] = chat_history
            
            response = requests.post(f"{BACKEND_URL}/chat", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to chat with documents: {str(e)}")

    @staticmethod
    def check_health() -> bool:
        """Check if the backend is running."""
        try:
            response = requests.get(f"{BACKEND_URL}/health")
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False
