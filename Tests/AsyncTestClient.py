import asyncio
import json
import socket
from typing import Dict, Any


class AsyncTestClient:
    def __init__(self, socket_path: str = '/tmp/my_socket'):
        self.SOCKET_PATH = socket_path

    async def send_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Отправляет запрос на сервер и возвращает ответ"""
        try:
            reader, writer = await asyncio.open_unix_connection(self.SOCKET_PATH)
            
            # Отправляем запрос
            request_json = json.dumps(request_data)
            writer.write(request_json.encode())
            await writer.drain()
            
            # Читаем ответ
            data = await reader.read(4096)
            writer.close()
            await writer.wait_closed()
            
            response = json.loads(data.decode())
            return response
            
        except Exception as e:
            return {'error': f'Client error: {str(e)}'}


async def run_tests():
    """Запускает тестовые запросы"""
    client = AsyncTestClient()
    
    # Тестовые случаи
    test_cases = [
        # Корректные запросы
        {'exchange_id': 1, 'coin_id': 1},
        {'exchange_id': 2, 'coin_id': 2},
        
        # Некорректные запросы
        {'exchange_id': 999, 'coin_id': 999},  # Несуществующие ID
        {'exchange_id': 'invalid', 'coin_id': 1},  # Неправильный тип
        {'coin_id': 1},  # Отсутствует exchange_id
        {'exchange_id': 1},  # Отсутствует coin_id
        {'extra_field': 'value'},  # Лишние поля
        'invalid_string',  # Вообще не JSON объект
    ]
    
    print("Запуск тестов сервера...\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Тест {i}: {test_case}")
        
        try:
            response = await client.send_request(test_case)
            print(f"Ответ: {response}")
        except Exception as e:
            print(f"Ошибка: {e}")
        
        print("-" * 50)


async def interactive_test():
    """Интерактивное тестирование"""
    client = AsyncTestClient()
    
    print("Интерактивный режим тестирования")
    print("Введите exchange_id и coin_id (через пробел) или 'quit' для выхода")
    
    while True:
        try:
            user_input = input("\nВвод: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
                
            parts = user_input.split()
            if len(parts) != 2:
                print("Ошибка: нужно ввести два числа через пробел")
                continue
                
            try:
                exchange_id = int(parts[0])
                coin_id = int(parts[1])
                
                request = {'exchange_id': exchange_id, 'coin_id': coin_id}
                print(f"Отправка: {request}")
                
                response = await client.send_request(request)
                print(f"Ответ: {response}")
                
            except ValueError:
                print("Ошибка: оба значения должны быть числами")
                
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Ошибка: {e}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        asyncio.run(interactive_test())
    else:
        asyncio.run(run_tests())