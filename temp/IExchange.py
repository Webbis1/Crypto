from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IExchange(ABC):
    """Абстрактный класс для работы с биржей криптовалют"""
    
    def __init__(self, api_key: str, api_secret: str, password: Optional[str] = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.password = password
    
    # @abstractmethod
    # def get_balance(self) -> Dict[str, float]:
    #     """
    #     Получить баланс по всем валютам
        
    #     Returns:
    #         Словарь с балансами в формате {валюта: количество}
    #     """
    #     pass
    
    # @abstractmethod
    # def get_currency_balance(self, currency: str) -> float:
    #     """
    #     Получить баланс по конкретной валюте
        
    #     Args:
    #         currency: Код валюты (например, 'BTC', 'ETH', 'USDT')
            
    #     Returns:
    #         Количество указанной валюты на счете
    #     """
    #     pass
    
    # @abstractmethod
    # def create_buy_order(self, pair: str, quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
    #     """
    #     Создать ордер на покупку
        
    #     Args:
    #         pair: Торговая пара (например, 'BTC/USDT')
    #         quantity: Количество базовой валюты для покупки
    #         price: Цена (если None - рыночный ордер)
            
    #     Returns:
    #         Информация о созданном ордере
    #     """
    #     pass
    
    # @abstractmethod
    # def create_sell_order(self, pair: str, quantity: float, price: Optional[float] = None) -> Dict[str, Any]:
    #     """
    #     Создать ордер на продажу
        
    #     Args:
    #         pair: Торговая пара (например, 'BTC/USDT')
    #         quantity: Количество базовой валюты для продажи
    #         price: Цена (если None - рыночный ордер)
            
    #     Returns:
    #         Информация о созданном ордере
    #     """
    #     pass
    
    # @abstractmethod
    # def get_order_status(self, order_id: str) -> Dict[str, Any]:
    #     """
    #     Получить статус ордера
        
    #     Args:
    #         order_id: ID ордера
            
    #     Returns:
    #         Информация о статусе ордера
    #     """
    #     pass
    
    # @abstractmethod
    # def cancel_order(self, order_id: str) -> bool:
        """
        Отменить ордер
        
        Args:
            order_id: ID ордера
            
        Returns:
            True если ордер успешно отменен, иначе False
        """
        pass