from dataclasses import dataclass, field
from itertools import count
from .Exchange import Exchange
from typing import ClassVar

coin_counter = count(1)

@dataclass(eq=False)
class Coin:
    # Статический словарь для хранения всех монет
    #_registry: dict[int, 'Coin'] = field(default_factory=dict)
    _registry: ClassVar[dict[int, 'Coin']] = {}
    
    name: str = field(default_factory=str)
    network: str = field(default_factory=str)
    id: int = field(default_factory=lambda: next(coin_counter))
    
    def __post_init__(self):
        # Автоматически регистрируем монету при создании
        self._registry[self.id] = self
    
    def __eq__(self, other) -> bool:
        if isinstance(other, Coin):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        else:
            return NotImplemented

    def __str__(self) -> str:
        return f'[{self.id}]:{self.name} in {self.network}'
    
    def __int__(self) -> int:
        return self.id

    def __hash__(self) -> int:
        return self.id 
    
    def set_name(self, name):
        self.name = name

    def set_network(self, network):
        self.network = network

    # Классовые методы для работы с реестром
    
    
    @classmethod
    def get_by_id(cls, coin_id: int) -> 'Coin | None':
        """Получить монету по ID"""
        return cls._registry.get(coin_id)
    
    @classmethod
    def get_by_name_and_network(cls, name: str, network: str) -> 'Coin | None':
        """Найти монету по имени и сети"""
        for coin in cls._registry.values():
            if coin.name == name and coin.network == network:
                return coin
        return None
    
    @classmethod
    def get_all_coins(cls) -> list['Coin']:
        """Получить все монеты"""
        return list(cls._registry.values())
    
    @classmethod
    def get_coins_by_network(cls, network: str) -> list['Coin']:
        """Получить все монеты в указанной сети"""
        return [coin for coin in cls._registry.values() if coin.network == network]
    
    @classmethod
    def count(cls) -> int:
        """Количество зарегистрированных монет"""
        return len(cls._registry)
    
    @classmethod
    def coin_exists(cls, coin_id: int) -> bool:
        """Проверить существует ли монета с таким ID"""
        return coin_id in cls._registry
    
    @classmethod
    def get_all_coin_names(cls) ->list[str]:
        return [coin.name for coin in Coin.get_all_coins()]
    
    