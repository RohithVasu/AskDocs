from pydantic import BaseModel
from typing import Any

class AppResponse(BaseModel):
    status: str
    message: str
    data: Any