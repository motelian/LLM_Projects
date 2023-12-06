from pydantic.dataclasses import dataclass
from typing import List, Optional, Any


@dataclass
class Message:
    role:str
    content:str


@dataclass
class LLMResponse:
    """Response from a Large Language Model"""

    text: List[Message]
    config: Any
    usage: Optional[Any] = None
    response: Optional[Any] = None # full response object
