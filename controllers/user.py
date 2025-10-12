from dataclasses import dataclass, field
from typing import List

@dataclass
class User:
    id: str
    name: str
    email: str
    borrowed: List[str] = field(default_factory=list)
