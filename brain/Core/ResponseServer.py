import socket
import json
import os
import asyncio
from typing import Dict, Any, Optional, Callable
from .Analyst import Analyst
from .Types import Exchange, Coin


class AsyncResponseServer:
    def __init__(self, processor_instance: Analyst, buffer_size: int = 4096, socket_path: str = '/tmp/my_socket'):
        self.SOCKET_PATH = socket_path
        self.BUFFER_SIZE = buffer_size
        self.processor: Analyst = processor_instance
        self.server = None

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Асинхронная обработка клиента"""
        try:
            # Читаем все данные
            data = await reader.read(self.BUFFER_SIZE)
            
            if not data:
                writer.write(b'{"error": "No data received"}')
                await writer.drain()
                return
            
            try:
                request_json = json.loads(data.decode())
                print(f"Получен запрос: {request_json}")
                
                # Проверяем что пришло ровно две строки
                if not self._validate_request(request_json):
                    error_response = {
                        'error': 'Invalid request format',
                        'message': 'Ожидалось ровно две строки: exchange_id и coin_id'
                    }
                    writer.write(json.dumps(error_response).encode())
                    await writer.drain()
                    return
                
                # Обрабатываем запрос через переданный класс
                exchange_id: int = request_json.get('exchange_id')
                coin_id:int = request_json.get('coin_id')
                
                
                response = await self.processor.analyse(Exchange.get_by_id(exchange_id), Coin.get_by_id(coin_id))
                
                # Отправляем ответ
                response_bytes = json.dumps(response).encode()
                writer.write(response_bytes)
                await writer.drain()
                print(f"Отправлен ответ: {response}")
                
            except json.JSONDecodeError as e:
                error_response = {
                    'error': 'Invalid JSON', 
                    'message': str(e)
                }
                writer.write(json.dumps(error_response).encode())
                await writer.drain()
                
        except Exception as e:
            print(f"Ошибка в обработчике: {e}")
            try:
                error_response = {'error': 'Internal server error', 'message': str(e)}
                writer.write(json.dumps(error_response).encode())
                await writer.drain()
            except:
                pass
        finally:
            writer.close()
            await writer.wait_closed()

    def _validate_request(self, request_data: Dict[str, Any]) -> bool:
        """Проверяем что пришло ровно две строки: exchange_id и coin_id"""
        if not isinstance(request_data, dict):
            return False
        
        # Должны быть ровно два ключа
        if len(request_data) != 2:
            return False
        
        # Должны быть ключи 'name' и 'coin_id'
        if 'exchange_id' not in request_data or 'coin_id' not in request_data:
            return False
        
        # Оба значения должны быть строками
        exchange_id = request_data.get('exchange_id')
        coin_id = request_data.get('coin_id')
        
        if not isinstance(exchange_id, int) or not isinstance(coin_id, int):
            return False
        
        if Exchange.get_by_id(exchange_id) is None:
            return False
        
        if Coin.get_by_id(coin_id) is None:
            return False
        
        
        return True

    async def start_async_server(self):
        """Запуск асинхронного сервера"""
        # Удаляем старый сокет если существует
        if os.path.exists(self.SOCKET_PATH):
            os.unlink(self.SOCKET_PATH)
            
        # Создаем директорию если нужно
        socket_dir = os.path.dirname(self.SOCKET_PATH)
        if socket_dir and not os.path.exists(socket_dir):
            os.makedirs(socket_dir, mode=0o755, exist_ok=True)
            
        self.server = await asyncio.start_unix_server(
            self.handle_client,
            path=self.SOCKET_PATH
        )
        
        # Устанавливаем права на сокет
        os.chmod(self.SOCKET_PATH, 0o666)
        
        print(f"Async сервер запущен на {self.SOCKET_PATH}")
        
        async with self.server:
            await self.server.serve_forever()

    def stop_server(self):
        """Остановка сервера"""
        if self.server:
            self.server.close()
        if os.path.exists(self.SOCKET_PATH):
            os.unlink(self.SOCKET_PATH)
        print("Сервер остановлен")