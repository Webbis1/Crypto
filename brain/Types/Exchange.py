from dataclasses import dataclass, field
from itertools import count

exchange_counter = count(1)

@dataclass(eq=False)
class Exchange:
    # Статическая переменная - реестр всех бирж
    _registry: dict[int, 'Exchange'] = {}
    
    name: str
    id: int = field(default_factory=lambda: next(exchange_counter))
    
    def __post_init__(self):
        # Автоматически регистрируем при создании
        self._registry[self.id] = self
    
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
    
    # Статический метод для получения биржи по ID
    @classmethod
    def get_by_id(cls, exchange_id: int) -> 'Exchange | None':
        return cls._registry.get(exchange_id)
    
    # Статический метод для получения всех бирж
    @classmethod
    def get_all(cls) -> list['Exchange']:
        return list(cls._registry.values())
    
    # Статический метод для количества бирж
    @classmethod
    def count(cls) -> int:
        return len(cls._registry)