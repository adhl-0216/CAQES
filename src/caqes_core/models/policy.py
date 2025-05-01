from pydantic import BaseModel
from typing import List

class Policy(BaseModel):
    name: str
    description: str
    rules: List[str]
    
  