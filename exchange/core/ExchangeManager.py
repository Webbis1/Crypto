import socket
import json
from typing import Dict, Optional, Any, AsyncIterator
from typing import Dict
import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class Assets:
    currency: str
    amount: float

@dataclass
class Destination:
    address: str
    network: str

class BalanceMonitor(ABC):
    @abstractmethod
    async def receive_all(self) -> AsyncIterator[Assets]:
        pass


class ExchangeManager:
    
    SOCKET_PATH = '/tmp/my_socket'
    BUFFER_SIZE = 4096
    
    def __init__(self, name: str, balanceMonitor: BalanceMonitor, limit: int = 5):
        self.limit = limit
        self.name = name
        self.balanceMonitor = balanceMonitor
        self.reserve: Dict[str, float] = {}
        self._running = True
     
    async def start_monitoring(self):
        asyncio.create_task(self._balance_monitoring_loop())
    
    async def _balance_monitoring_loop(self):
        async for asset_update in self.balance_monitor.receive_all():
            if not self._running:
                break
            await self._process_asset_update(asset_update)
    
    async def _process_asset_update(self, asset_update: Assets):
        currency = asset_update.currency
        amount = asset_update.amount
        
        current = self.reserve.get(currency, 0.0)
        self.reserve[currency] = max(0.0, current - amount)
        
        excess_amount = max(0.0, amount - current)
        if excess_amount > 0:
            response = await self.consultation(currency)
            await self._handle_response(response, Assets(currency, excess_amount))
        
    def _send_json_request(self, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        try:
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
                client.settimeout(10.0)
                client.connect(self.SOCKET_PATH)
                
                message = json.dumps(data).encode()
                client.sendall(message)
                
                response_data = b""
                while True:
                    chunk = client.recv(self.BUFFER_SIZE)
                    if not chunk:
                        break
                    response_data += chunk

                    if len(chunk) < self.BUFFER_SIZE:
                        break
                
                if response_data:
                    return json.loads(response_data.decode())
                return None
                
        except (socket.timeout, ConnectionError) as e:
            print(f"Сетевая ошибка: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Ошибка парсинга JSON: {e}")
            return None
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return None
        
    async def _handle_response(self, response: Optional[Dict[str, Any]], assets: Assets):
        if not response:
            print("Предупреждение: Нет ответа от сервера")
            return
        
        recommendation = response.get('recommendation')
        
        handlers = {
            'trade': self._handle_trade,
            'transfer': self._handle_transfer, 
            'wait': self._handle_wait,
            'shutdown': self._handle_shutdown
        }
        
        handler = handlers.get(recommendation)
        if handler:
            await handler(response, assets)
        else:
            print(f"Неизвестная рекомендация: {recommendation}")

    async def _handle_trade(self, response: Dict[str, Any], assets: Assets):
        if 'buying' not in response:
            raise ValueError("Нет информации о покупке в ответе сервера")
        
        # TODO: добавить контроль лимита
        await self.trade(assets, response['buying'])

    async def _handle_transfer(self, response: Dict[str, Any], assets: Assets):
        destination_info = response.get('destination', {})
        
        if not all(key in destination_info for key in ['address', 'network']):
            raise ValueError("Недостаточно информации о пункте назначения")
        
        destination = Destination(
            address=destination_info['address'],
            network=destination_info['network']
        )
        await self.transfer(assets, destination)

    async def _handle_wait(self, response: Dict[str, Any], assets: Assets):
        if 'time' not in response:
            raise ValueError("Нет времени ожидания в ответе сервера")
        
        await asyncio.sleep(response['time'])
        new_response = await self.consultation(assets.currency)
        await self._handle_response(new_response, assets)

    async def _handle_shutdown(self, response: Dict[str, Any], assets: Assets):
        self._running = False
        print("Получена команда выключения")    
          
    # перевод средств
    async def transfer(self, celling: Assets, destination: Destination):
        pass

    # продажа средств
    async def trade(self, celling: Assets, buying: str): 
        pass

    async def consultation(self, currency: str) -> Optional[Dict[str, Any]]:
        data = {
            "name": self.name,
            "currency": currency
        }
        return self._send_json_request(data)
        
    async def stop(self):
        self._running = False
    
    async def __aenter__(self):
        await self.start_monitoring()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.stop()