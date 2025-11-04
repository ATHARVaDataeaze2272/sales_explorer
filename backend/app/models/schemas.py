from pydantic import BaseModel
from typing import Dict, Any

class ProcessRequest(BaseModel):
    bucket: str
    excluded_pages: Dict[str, str]  # filename: excluded_pages_str

class ProcessResponse(BaseModel):
    success: bool
    message: str
    data: Any = None