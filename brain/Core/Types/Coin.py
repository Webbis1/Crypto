from dataclasses import dataclass, field
from typing import final
import copy

@dataclass
class Coin:
    _id: int = field(init=False)
    _name: str
    _counter = 0
    
    def __post_init__(self):
        if not hasattr(self, '_id'):
            type(self)._counter += 1
            self._id = type(self)._counter
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Coin):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        else:
            return NotImplemented
        
    def __hash__(self) -> int:
        return self.id
    
    def __copy__(self):
        """Поверхностное копирование - сохраняет ID"""
        new_coin = Coin(self._name)
        # print(f"Old coin - {self.name} and new coin {new_coin}")
        new_coin._id = self._id  # ⚡ Сохраняем оригинальный ID
        return new_coin
    
    def __deepcopy__(self, memo):
        """Глубокое копирование - сохраняет ID"""
        new_coin = Coin(copy.deepcopy(self._name, memo))
        
        # print(f"Old coin - {self.name} and new coin {new_coin}")
        new_coin._id = self._id  # ⚡ Сохраняем оригинальный ID
        return new_coin