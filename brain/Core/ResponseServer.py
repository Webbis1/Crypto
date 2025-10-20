import socket
import json
import os
import asyncio
import logging
from typing import Dict, Any, Optional, Callable
from .Analyst import Analyst
from .Types import Exchange, Coin

logger = logging.getLogger('main')

class AsyncResponseServer:
    def __init__(self, processor_instance: Analyst, buffer_size: int = 4096, socket_path: str = '/tmp/my_socket'):
        self.SOCKET_PATH = socket_path
        self.BUFFER_SIZE = buffer_size
        self.processor: Analyst = processor_instance
        self.server = None
        self._is_running = False

    async def __aenter__(self):
        """Асинхронный контекстный менеджер для входа"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер для выхода - автоматическая остановка сервера"""
        await self.stop_server()
        if exc_type is not None:
            logger.error(f"AsyncResponseServer завершился с ошибкой: {exc_type.__name__}: {exc_val}")
        return False

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Асинхронная обработка клиента"""
        client_info = ""
        try:
            # Получаем информацию о клиенте
            try:
                client_info = f"client_{writer.get_extra_info('peername')}"
            except:
                client_info = "unknown_client"
            
            # Читаем все данные
            data = await reader.read(self.BUFFER_SIZE)
            
            if not data:
                writer.write(b'{"error": "No data received"}')
                await writer.drain()
                return
            
            try:
                request_json = json.loads(data.decode())
                logger.debug(f"Получен запрос от {client_info}: {request_json}")
                
                # Проверяем что пришло ровно две строки
                if not self._validate_request(request_json):
                    error_response = {
                        'error': 'Invalid request format',
                        'message': 'Ожидалось ровно две строки: exchange_id и coin_id'
                    }
                    writer.write(json.dumps(error_response).encode())
                    await writer.drain()
                    logger.warning(f"Неверный формат запроса от {client_info}")
                    return
                
                # Обрабатываем запрос через переданный класс
                exchange_id: int = request_json.get('exchange_id')
                coin_id: int = request_json.get('coin_id')
                
                # Используем существующий processor, а не создаем новый контекст
                response = await self.processor.analyse(Exchange.get_by_id(exchange_id), Coin.get_by_id(coin_id))
                
                # Отправляем ответ
                response_bytes = json.dumps(response).encode()
                writer.write(response_bytes)
                await writer.drain()
                logger.debug(f"Отправлен ответ {client_info}: успешно обработан запрос")
                
            except json.JSONDecodeError as e:
                error_response = {
                    'error': 'Invalid JSON', 
                    'message': str(e)
                }
                writer.write(json.dumps(error_response).encode())
                await writer.drain()
                logger.warning(f"Невалидный JSON от {client_info}: {e}")
                
        except Exception as e:
            logger.error(f"Ошибка при обработке клиента {client_info}: {e}")
            try:
                error_response = {'error': 'Internal server error', 'message': str(e)}
                writer.write(json.dumps(error_response).encode())
                await writer.drain()
            except Exception as inner_e:
                logger.error(f"Ошибка при отправке ошибки клиенту {client_info}: {inner_e}")
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception as e:
                logger.debug(f"Ошибка при закрытии соединения с {client_info}: {e}")

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
        if self._is_running:
            logger.warning("Сервер уже запущен")
            return
            
        # Удаляем старый сокет если существует
        if os.path.exists(self.SOCKET_PATH):
            os.unlink(self.SOCKET_PATH)
            
        # Создаем директорию если нужно
        socket_dir = os.path.dirname(self.SOCKET_PATH)
        if socket_dir and not os.path.exists(socket_dir):
            os.makedirs(socket_dir, mode=0o755, exist_ok=True)
            
        try:
            self.server = await asyncio.start_unix_server(
                self.handle_client,
                path=self.SOCKET_PATH
            )
            
            # Устанавливаем права на сокет
            os.chmod(self.SOCKET_PATH, 0o666)
            
            self._is_running = True
            logger.info(f"Async сервер запущен на {self.SOCKET_PATH}")
            
            async with self.server:
                await self.server.serve_forever()
                
        except Exception as e:
            logger.error(f"Ошибка при запуске сервера: {e}")
            raise
        finally:
            self._is_running = False

    async def stop_server(self):
        """Остановка сервера"""
        if not self._is_running:
            return
            
        logger.info("Останавливаем async сервер...")
        self._is_running = False
        
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.debug("Сервер закрыт")
        
        if os.path.exists(self.SOCKET_PATH):
            try:
                os.unlink(self.SOCKET_PATH)
                logger.debug("Сокет файл удален")
            except Exception as e:
                logger.warning(f"Не удалось удалить сокет файл: {e}")
        
        logger.info("Сервер полностью остановлен")