from dataclasses import dataclass
from itertools import count

exchange_counter = count(1)

@dataclass(eq=False)
class Exchange:
    name: str = ""
    id: int = 0
    
    def __post_init__(self):
        if self.id == 0:
            self.id = next(exchange_counter)
        # Инициализируем реестр, если его нет
        if not hasattr(Exchange, '_registry'):
            Exchange._registry = {}
        Exchange._registry[self.id] = self
    
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
    
    def set_name(self, name: str) -> None:
        self.name = name
    
    @classmethod
    def get_by_id(cls, exchange_id: int) -> 'Exchange | None':
        return getattr(cls, '_registry', {}).get(exchange_id)
    
    @classmethod
    def get_all(cls) -> list['Exchange']:
        return list(getattr(cls, '_registry', {}).values())
    
    @classmethod
    def count(cls) -> int:
        return len(getattr(cls, '_registry', {}))