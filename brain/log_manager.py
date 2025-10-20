# log_manager.py
import logging
import multiprocessing as mp
from multiprocessing import Queue
from pathlib import Path
from typing import Dict, Any
import time
import atexit

class MultiFileLogWorker:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        # Создаем поддиректории
        (self.log_dir / "scouts").mkdir(exist_ok=True)
        (self.log_dir / "analyst").mkdir(exist_ok=True)
        (self.log_dir / "exchanges").mkdir(exist_ok=True)
        self.log_queue = Queue()
        self.process = None
        self._stop_signal = mp.Event()
    
    def start(self):
        """Запуск рабочего процесса"""
        self.process = mp.Process(
            target=self._worker_loop,
            args=(self.log_queue, str(self.log_dir), self._stop_signal)
        )
        self.process.daemon = True
        self.process.start()
        return self.log_queue
    
    def stop(self):
        """Корректная остановка рабочего процесса"""
        if self.process and self.process.is_alive():
            self.log_queue.put(None)  # Сигнал остановки
            self.process.join(timeout=5)
            if self.process.is_alive():
                self.process.terminate()
    
    @staticmethod
    def _worker_loop(log_queue: Queue, log_dir: str, stop_signal):
        """Цикл рабочего процесса с разными файлами"""
        log_path = Path(log_dir)
        
        # Создаем все необходимые поддиректории
        (log_path / "scouts").mkdir(exist_ok=True)
        (log_path / "analyst").mkdir(exist_ok=True)
        (log_path / "exchanges").mkdir(exist_ok=True)
        
        loggers = {}
        
        def get_logger(name: str) -> logging.Logger:
            if name not in loggers:
                logger = logging.getLogger(name)
                logger.setLevel(logging.DEBUG)
                
                # Определяем путь к файлу в зависимости от типа логгера
                if name.startswith('scout.'):
                    scout_name = name.split('.')[-1]
                    log_file = log_path / "scouts" / f"{scout_name}.log"
                elif name.startswith('analyst'):
                    log_file = log_path / "analyst.log"
                elif name.startswith('exchange'):
                    log_file = log_path / "exchanges.log"
                else:
                    log_file = log_path / f"{name}.log"
                
                file_handler = logging.FileHandler(
                    log_file, 
                    encoding='utf-8',
                    mode='a'
                )
                
                formatter = logging.Formatter(
                    '%(asctime)s | %(levelname)-8s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(formatter)
                
                logger.addHandler(file_handler)
                logger.propagate = False
                loggers[name] = logger
            
            return loggers[name]
        
        # Общий логгер для всех сообщений
        general_logger = logging.getLogger('general')
        general_logger.setLevel(logging.INFO)
        
        general_handler = logging.FileHandler(
            log_path / "general.log", 
            encoding='utf-8'
        )
        general_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(name)-15s | %(levelname)-8s | %(message)s'
        ))
        general_logger.addHandler(general_handler)
        
        # Обработчик ошибок
        error_logger = logging.getLogger('errors')
        error_logger.setLevel(logging.ERROR)
        
        error_handler = logging.FileHandler(
            log_path / "errors.log",
            encoding='utf-8'
        )
        error_handler.setFormatter(logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)s | %(message)s\n%(pathname)s:%(lineno)d'
        ))
        error_logger.addHandler(error_handler)
        
        print(f"🎯 Log worker started. Logs directory: {log_path.absolute()}")
        
        while not stop_signal.is_set():
            try:
                # Используем timeout для периодической проверки stop_signal
                record_data = log_queue.get(timeout=1.0)
                
                if record_data is None:
                    break
                
                record = logging.makeLogRecord(record_data)
                logger_name = record.name
                
                if logger_name.startswith('scout.'):
                    scout_name = logger_name.split('.')[-1]
                    logger = get_logger(f"scout.{scout_name}")
                elif logger_name.startswith('analyst'):
                    logger = get_logger("analyst")
                elif logger_name.startswith('exchange'):
                    logger = get_logger("exchanges")
                else:
                    logger = general_logger
                
                logger.handle(record)
                
                if record.levelno >= logging.ERROR:
                    error_logger.handle(record)
                    
            except Exception as e:
                # Игнорируем timeout от queue.get()
                if not isinstance(e, mp.queues.Empty):
                    print(f"❌ Log worker error: {e}")
        
        print("🛑 Log worker stopped")

class AsyncLogManager:
    def __init__(self, log_dir: str = "logs"):
        self.log_worker = MultiFileLogWorker(log_dir)
        self.log_queue = self.log_worker.start()
        self._setup_main_loggers()
        atexit.register(self.stop)
    
    def _setup_main_loggers(self):
        """Настройка логгеров в основном процессе"""
        
        class AsyncHandler(logging.Handler):
            def __init__(self, log_queue):
                super().__init__()
                self.log_queue = log_queue
            
            def emit(self, record):
                try:
                    # ФИЛЬТРУЕМ DEBUG логи от внешних библиотек
                    if record.levelno >= logging.INFO:
                        self.log_queue.put(record.__dict__)
                except Exception:
                    pass  # Игнорируем ошибки при логировании
        
        # Создаем быстрый обработчик для основного процесса
        handler = AsyncHandler(self.log_queue)
        handler.setLevel(logging.INFO)  # ТОЛЬКО INFO И ВЫШЕ
        
        # Применяем ко всем логгерам
        root_logger = logging.getLogger()
        root_logger.addHandler(handler)
        root_logger.setLevel(logging.INFO)  # ТОЛЬКО INFO И ВЫШЕ
        
        # ВАЖНО: Отключаем ВСЕ debug логи от внешних библиотек
        for name in logging.Logger.manager.loggerDict:
            if not name.startswith(('main', 'scout', 'analyst', 'scout_dad')):
                logging.getLogger(name).setLevel(logging.WARNING)
        
        # Создаем основные логгеры для разных компонентов
        self._create_component_loggers()
    
    def _create_component_loggers(self):
        """Создаем предварительно логгеры для всех компонентов"""
        components = {
            'main': logging.getLogger('main'),
            'scout_dad': logging.getLogger('scout_dad'),
            'analyst': logging.getLogger('analyst'),
            # Скауты
            'scout.bybit': logging.getLogger('scout.bybit'),
            'scout.kucoin': logging.getLogger('scout.kucoin'), 
            'scout.gate': logging.getLogger('scout.gate'),
            'scout.okx': logging.getLogger('scout.okx'),
            'scout.bitget': logging.getLogger('scout.bitget'),
            # Общие
            'general': logging.getLogger('general'),
            'errors': logging.getLogger('errors')
        }
        
        # Устанавливаем уровни для разных компонентов
        components['main'].setLevel(logging.INFO)
        components['scout_dad'].setLevel(logging.INFO)
        components['analyst'].setLevel(logging.INFO)
        
        for scout_name in ['bybit', 'kucoin', 'gate', 'okx', 'bitget']:
            components[f'scout.{scout_name}'].setLevel(logging.INFO)
    
    def stop(self):
        """Корректная остановка менеджера логов"""
        self.log_worker.stop()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()