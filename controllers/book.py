from collections import deque
from dataclasses import dataclass, field

@dataclass
class Book:
    id: str
    title: str
    author: str
    year: int
    copies_total: int
    copies_available: int = field(init=False)
    reservations: deque = field(default_factory=deque)  # cola de usuarios en espera

    def __post_init__(self):
        self.copies_available = self.copies_total
