from dataclasses import dataclass
from itertools import count
from .Coin import Coin
from copy import deepcopy, copy
from typing import Optional

exchange_counter = count(1)

@dataclass(eq=False)
class Exchange:
    name: str = ""
    _coins: list[Coin] = None
    _id: int = 0
    
    def __post_init__(self):
        if self._id == 0:
            self._id = next(exchange_counter)
        # Инициализируем реестр, если его нет
        if not hasattr(Exchange, '_registry'):
            Exchange._registry = {}
        Exchange._registry[self._id] = self
        
        # Инициализация списка coins
        self._coins = []
        if self.coins:
            self._coins = [deepcopy(coin) for coin in self.coins]
    
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
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, value):
        self._name = value
        
    @property
    def id(self):
        return self._id
    
    @id.setter
    def id(self, value):
        self._id = value
    
    @property
    def coins(self) -> list[Coin]:
        """Геттер возвращает глубокую копию списка coins"""
        return self._coins
    
    @coins.setter
    def coins(self, new_coins: list[Coin]):
        """Сеттер устанавливает новый список coins, создавая глубокие копии"""
        # print("add coins")
        self._coins = [copy(coin) for coin in new_coins] if new_coins else []
    
    def add_coin(self, coin: Coin):
        """Метод для добавления одной монеты (с созданием глубокой копии)"""
        self._coins.append(deepcopy(coin))
    
    def get_coin_by_name(self, name: str) -> Optional[Coin]:
        """Возвращает монету по имени (глубокую копию)"""
        for coin in self._coins:
            if coin.name == name:
                return coin
        return None
    
    def get_coins_by_name(self, name: str) -> list[Coin]:
        """Возвращает все монеты с указанным именем (глубокие копии)"""
        return [deepcopy(coin) for coin in self._coins if coin.name == name]
    
    def has_coin_with_name(self, name: str) -> bool:
        """Проверяет, есть ли монета с указанным именем"""
        return any(coin.name == name for coin in self._coins)
    
    def remove_coin_by_name(self, name: str) -> bool:
        """Удаляет первую найденную монету с указанным именем"""
        for i, coin in enumerate(self._coins):
            if coin.name == name:
                del self._coins[i]
                return True
        return False
    
    def remove_all_coins_by_name(self, name: str) -> int:
        """Удаляет все монеты с указанным именем и возвращает количество удаленных"""
        initial_length = len(self._coins)
        self._coins = [coin for coin in self._coins if coin.name != name]
        return initial_length - len(self._coins)
    
    def __getitem__(self, index):
        """Доступ к отдельным элементам также возвращает копии"""
        return deepcopy(self._coins[index])
    
    def __len__(self):
        return len(self._coins)
    
    def __repr__(self):
        return f"Exchange(id={self.id}, name='{self.name}', coins={self._coins})"
    
    @classmethod
    def get_by_id(cls, exchange_id: int) -> 'Exchange | None':
        return getattr(cls, '_registry', {}).get(exchange_id)
    
    @classmethod
    def get_all(cls) -> list['Exchange']:
        return list(getattr(cls, '_registry', {}).values())
    
    @classmethod
    def count(cls) -> int:
        return len(getattr(cls, '_registry', {}))