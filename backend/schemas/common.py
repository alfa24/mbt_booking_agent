from typing import Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[list] = None
