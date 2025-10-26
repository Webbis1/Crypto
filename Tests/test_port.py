import pytest
import pytest_asyncio
import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, patch
import ccxt
import ccxt.pro as ccxtpro

try:
    from Exchange2.Types.Port import Port
    from Exchange2.Types.ExFactory import ExFactory, ExchangeConnectionError
except ImportError as e:
    # Этот блок поможет отладить, если Python не может найти модули
    print(f"Failed to import modules: {e}")
    print("Please ensure 'port_module.py' and 'ExFactory.py' are in your PYTHONPATH,")
    print("or run pytest from the project root directory.")
    # Для целей тестирования можно пропустить тесты, если импорт не удался
    pytest.fail("Module import failed. Check project structure and PYTHONPATH.")


# Настройка логгирования для тестов
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# --- Фикстуры для моков ---

@pytest_asyncio.fixture
async def mock_ex_factory():
    """Фикстура для создания мок-объекта ExFactory."""
    factory = MagicMock()
    
    # Binance mock
    binance_ex_mock = AsyncMock() # Без spec для большей гибкости с ccxt
    binance_ex_mock.id = 'binance'
    binance_ex_mock.fetchDepositAddress.return_value = {'currency': 'USDT', 'address': 'binance_usdt_address_trc20', 'tag': None, 'network': 'TRC20'}
    
    # Bybit mock
    bybit_ex_mock = AsyncMock()
    bybit_ex_mock.id = 'bybit'

    # OKX mock
    okx_ex_mock = AsyncMock()
    okx_ex_mock.id = 'okx'

    # Настраиваем, что возвращает фабрика при запросе биржи
    factory.get.side_effect = lambda key: {
        "binance": binance_ex_mock,
        "bybit": bybit_ex_mock,
        "okx": okx_ex_mock
    }.get(key, None)
    
    # Также настроим __getitem__ на случай, если Port использует factory[...] вместо factory.get(...)
    factory.__getitem__.side_effect = lambda key: {
        "binance": binance_ex_mock,
        "bybit": bybit_ex_mock,
        "okx": okx_ex_mock
    }[key] # Здесь KeyError, если биржа не найдена, имитируя поведение словаря
    
    return factory

@pytest.fixture
def sample_routes():
    """Фикстура для создания тестовых маршрутов."""
    return {
        "binance": {
            1: {"TRC20": "TRX", "BSC": "BSC"}, # USDT (id=1) на Binance
            2: {"ERC20": "ETH"} # ETH (id=2) на Binance
        },
        "bybit": {
            1: {"ERC20": "ETH", "ARBITRUM": "ARBITRUM"} # USDT (id=1) на Bybit
        },
        "okx": {
            3: {"AVAXC": "AVAXC"} # AVAX (id=3) на OKX
        }
    }

@pytest_asyncio.fixture
async def port_instance(mock_ex_factory, sample_routes):
    """Фикстура для создания экземпляра Port с мок-фабрикой."""
    return Port(mock_ex_factory, sample_routes)

# --- Юнит-тесты для Port.preparation ---

@pytest.mark.asyncio
async def test_preparation_successful(port_instance, mock_ex_factory):
    """Тест успешной подготовки Destination."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    assert destination.ex.id == "binance"
    assert destination.coin_name == "USDT"
    assert destination.chains == {"TRC20": "TRX", "BSC": "BSC"}
    mock_ex_factory.get.assert_called_with("binance")

@pytest.mark.asyncio
async def test_preparation_unknown_destination(port_instance, caplog):
    """Тест подготовки для неизвестной биржи."""
    with caplog.at_level(logging.WARNING):
        destination = await port_instance.preparation("unknown_exchange", (1, "USDT"))
        assert destination is None
        assert "Route for unknown_exchange not defined" in caplog.text

@pytest.mark.asyncio
async def test_preparation_unknown_coin_id(port_instance, caplog):
    """Тест подготовки для неизвестного ID монеты."""
    with caplog.at_level(logging.WARNING):
        destination = await port_instance.preparation("binance", (999, "UNKNOWN_COIN"))
        assert destination is None
        assert "Value for coin UNKNOWN_COIN (ID: 999) in route binance not defined" in caplog.text

@pytest.mark.asyncio
async def test_preparation_ex_factory_returns_none_for_exchange(port_instance, mock_ex_factory, caplog):
    """Тест, когда ExFactory возвращает None для биржи (несуществующая биржа в фабрике)."""
    # Заставляем mock_ex_factory.get возвращать None для "non_existent_exchange"
    # Добавляем маршрут, чтобы Port не отсекал его на первом этапе
    port_instance.routes["non_existent_exchange"] = {1: {"TRC20": "TRX"}} 
    mock_ex_factory.get.side_effect = lambda key: {
        "binance": mock_ex_factory.get("binance"),
        "bybit": mock_ex_factory.get("bybit"),
    }.get(key, None) # Убедимся, что по умолчанию возвращается None для всего остального

    with caplog.at_level(logging.WARNING):
        destination = await port_instance.preparation("non_existent_exchange", (1, "USDT"))
        assert destination is None
        assert "non_existent_exchange is an unknown destination or failed to initialize in ExFactory" in caplog.text


# --- Юнит-тесты для Port.Destination.get_deposit_address ---

@pytest.mark.asyncio
async def test_get_deposit_address_successful(port_instance):
    """Тест успешного получения адреса депозита."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    
    expected_address = 'binance_usdt_address_trc20'
    address = await destination.get_deposit_address("TRC20")
    
    assert address == expected_address
    destination.ex.fetchDepositAddress.assert_called_once_with("USDT", {'network': 'TRX', 'chain': 'TRX'})

@pytest.mark.asyncio
async def test_get_deposit_address_unsupported_departure_network(port_instance, caplog):
    """Тест получения адреса депозита для неподдерживаемой исходящей сети."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Сеть 'UNSUPPORTED' не поддерживается для USDT"):
            await destination.get_deposit_address("UNSUPPORTED")
        assert "Сеть 'UNSUPPORTED' не поддерживается для USDT" in caplog.text

@pytest.mark.asyncio
async def test_get_deposit_address_ccxt_bad_request_error(port_instance, caplog):
    """Тест ошибки ccxt.BadRequest при получении адреса депозита."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    
    destination.ex.fetchDepositAddress.side_effect = ccxt.BadRequest("Invalid network")
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Сеть TRX не поддерживается для USDT"):
            await destination.get_deposit_address("TRC20")
        assert "Сеть TRX не поддерживается для USDT: Invalid network" in caplog.text

@pytest.mark.asyncio
async def test_get_deposit_address_ccxt_base_error(port_instance, caplog):
    """Тест общей ошибки ccxt.BaseError при получении адреса депозита."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    
    destination.ex.fetchDepositAddress.side_effect = ccxt.ExchangeError("API down")
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ExchangeConnectionError, match="Ошибка подключения к бирже: API down"):
            await destination.get_deposit_address("TRC20")
        assert "Ошибка биржи при получении адреса USDT: API down" in caplog.text

@pytest.mark.asyncio
async def test_get_deposit_address_unexpected_exception(port_instance, caplog):
    """Тест непредвиденной ошибки при получении адреса депозита."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    
    destination.ex.fetchDepositAddress.side_effect = Exception("Something went wrong")
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(RuntimeError, match="Ошибка получения адреса: Something went wrong"):
            await destination.get_deposit_address("TRC20")
        assert "Неожиданная ошибка при получении адреса USDT: Something went wrong" in caplog.text

@pytest.mark.asyncio
async def test_get_deposit_address_empty_address_in_response(port_instance, caplog):
    """Тест, когда биржа возвращает ответ без адреса."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    
    destination.ex.fetchDepositAddress.return_value = {'currency': 'USDT', 'tag': None, 'network': 'TRC20'}
    
    with caplog.at_level(logging.ERROR):
        with pytest.raises(ValueError, match="Адрес не найден в ответе от биржи для USDT"):
            await destination.get_deposit_address("TRC20")

@pytest.mark.asyncio
async def test_get_deposit_address_with_addresses_list_in_response(port_instance):
    """Тест, когда биржа возвращает список адресов."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    
    destination.ex.fetchDepositAddress.return_value = {
        'currency': 'USDT', 
        'addresses': [{'address': 'address_from_list_1'}, {'address': 'address_from_list_2'}], 
        'tag': None, 
        'network': 'TRC20'
    }
    
    address = await destination.get_deposit_address("TRC20")
    assert address == 'address_from_list_1'

@pytest.mark.asyncio
async def test_get_deposit_address_string_response(port_instance):
    """Тест, когда биржа возвращает адрес напрямую как строку."""
    destination = await port_instance.preparation("binance", (1, "USDT"))
    assert destination is not None
    
    destination.ex.fetchDepositAddress.return_value = "simple_string_address"
    
    address = await destination.get_deposit_address("TRC20")
    assert address == "simple_string_address"