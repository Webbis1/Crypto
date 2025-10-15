from dataclasses import dataclass, field
from itertools import count

exchange_counter = count(1)

@dataclass(eq=False)
class Exchange:
    name: str
    id: int = field(default_factory=lambda: next(exchange_counter))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Exchange):
            return NotImplemented
        return self.id == other.id

    def __str__(self) -> str:
        return f'[{self.id}]:{self.name}'
    
    def __int__(self) -> int:
        return self.id
    
    def __hash__(self) -> int:
        return self.id 