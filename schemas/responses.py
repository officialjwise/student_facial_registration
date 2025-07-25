from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel

T = TypeVar('T')

class HTTPResponse(BaseModel, Generic[T]):
    """Standard HTTP response format."""
    message: str
    status_code: int
    count: Optional[int] = None
    data: Optional[List[T]] = None
