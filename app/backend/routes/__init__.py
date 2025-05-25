from pydantic import BaseModel
from typing import Dict

class ChatRequest(BaseModel):
    question: str
    collection_name: str

class AppResponse(BaseModel):
    time: str
    data: Dict