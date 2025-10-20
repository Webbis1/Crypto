from abc import ABC, abstractmethod
from .Assets import Assets
from .Destination import Destination

class Courier(ABC):
    @abstractmethod
    async def transfer(self, departure: str, celling: Assets, destination: Destination):
        """
        Абстрактный метод для выполнения асинхронного трансфера активов.
        
        Args:
            departure (str): Пункт отправления или идентификатор исходной локации
            celling (Assets): Максимально доступные для трансфера активы (лимиты)
            destination (Destination): Объект назначения, содержащий информацию 
                                     о точке прибытия и параметрах доставки
        
        Returns:
            None: Метод должен быть реализован в подклассах и выполнять операцию трансфера
            
        Raises:
            Различные исключения, связанные с конкретной реализацией курьера
            (например, ошибки сети, недостаточный баланс, недоступность пункта назначения)
        
        Note:
            Реализующие классы должны обеспечить корректную обработку всех параметров
            и гарантировать безопасность операции трансфера активов.
        """
        pass