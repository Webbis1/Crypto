from dataclasses import dataclass, field
from typing import Dict, Optional
import copy

@dataclass
class Coin:
    _id: int = field(init=False)
    _name: str
    
    def __post_init__(self):
        if not hasattr(self, '_id'):
            # Инициализируем статические атрибуты при первом использовании
            if not hasattr(self.__class__, '_counter'):
                self.__class__._counter = 0
            if not hasattr(self.__class__, '_coins_registry'):
                self.__class__._coins_registry = {}
                
            self.__class__._counter += 1
            self._id = self.__class__._counter
            # Сохраняем монету в реестр
            self.__class__._coins_registry[self._id] = self
    
    def __str__(self) -> str:
        return self._name
    
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
        return NotImplemented
        
    def __hash__(self) -> int:
        return self.id
    
    def __copy__(self):
        new_coin = Coin(self._name)
        new_coin._id = self._id
        return new_coin
    
    def __deepcopy__(self, memo):
        new_coin = Coin(copy.deepcopy(self._name, memo))
        new_coin._id = self._id
        return new_coin
    
    @classmethod
    def get_by_id(cls, coin_id: int) -> Optional['Coin']:
        return getattr(cls, '_coins_registry', {}).get(coin_id)
    
    @classmethod
    def get_all_coins(cls) -> Dict[int, 'Coin']:
        return getattr(cls, '_coins_registry', {}).copy()
    
    @classmethod
    def get_coins_count(cls) -> int:
        return len(getattr(cls, '_coins_registry', {}))
    
    @classmethod
    def clear_registry(cls):
        if hasattr(cls, '_coins_registry'):
            cls._coins_registry.clear()
        if hasattr(cls, '_counter'):
            cls._counter = 0