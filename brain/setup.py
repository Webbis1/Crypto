from Core.Types import *
from Core.scouts import *
from Core.Guide import Guide
import logging



def setup_loggers():
    return {
        'main': logging.getLogger('main'),
        'scout_dad': logging.getLogger('scout_dad'),
        'analyst': logging.getLogger('analyst'),
        'scouts': {
            'bybit': logging.getLogger('scout.bybit'),
            'kucoin': logging.getLogger('scout.kucoin'),
            'gate': logging.getLogger('scout.gate'),
            'okx': logging.getLogger('scout.okx'),
            'bitget': logging.getLogger('scout.bitget')
        }
    }

coin_list: list[Coin] = [
    Coin('USDT'),
    Coin('BTC'),
    Coin('ETH'),
    Coin('BNB'),
    Coin('SOL'),
    Coin('XRP'),
    Coin('ADA'),
    Coin('DOT'),
    Coin('DOGE'),
    Coin('AVAX'),
    Coin('MATIC'),
    Coin('LTC'),
    Coin('LINK'),
    Coin('ATOM'),
    Coin('UNI'),
    Coin('XLM'),
    Coin('ALGO'),
    Coin('NEAR'),
    Coin('FTM'),
    Coin('ETC'),
    Coin('BCH'),
    # Coin('XMR'),
    Coin('EOS'),
    Coin('AAVE'),
    Coin('MKR'),
    Coin('COMP'),
    Coin('YFI'),
    Coin('SUSHI'),
    Coin('CRV'),
    Coin('SNX'),
    Coin('RUNE'),
    Coin('GRT'),
    Coin('BAT'),
    Coin('ENJ'),
    Coin('MANA'),
    Coin('SAND'),
    Coin('AXS'),
    Coin('CHZ'),
    Coin('HBAR'),
    Coin('XTZ'),
    Coin('FIL'),
    Coin('THETA'),
    Coin('VET'),
    Coin('ICP'),
    Coin('FLOW'),
    Coin('EGLD'),
    Coin('KLAY'),
    Coin('ONE'),
    Coin('CELO'),
    Coin('IOTA'),
    Coin('ZIL'),
    Coin('WAVES'),
    Coin('NEO'),
    # Coin('ZEC'),
    # Coin('DASH'),
    Coin('QTUM'),
    Coin('ONT'),
    Coin('SC'),
    Coin('BTT'),
    Coin('WIN'),
    Coin('JST'),
    Coin('SUN'),
    Coin('ANKR'),
    Coin('OCEAN'),
    Coin('BAND'),
    Coin('OMG'),
    Coin('ZRX'),
    Coin('KAVA'),
    Coin('INJ'),
    Coin('ROSE'),
    Coin('IOTX'),
    Coin('AUDIO'),
    Coin('RSR'),
    Coin('COTI'),
    Coin('DODO'),
    Coin('PERP'),
    Coin('TRB'),
    Coin('UMA'),
    Coin('REN'),
    Coin('KNC'),
    Coin('REQ'),
    Coin('ORN'),
    Coin('TOMO'),
    Coin('DGB'),
    Coin('ICX'),
    Coin('AR'),
    Coin('RVN'),
    Coin('CELR'),
    Coin('SKL'),
    Coin('OGN'),
    Coin('CVC'),
    Coin('STORJ'),
    Coin('DATA'),
    Coin('ANT'),
    Coin('MIR'),
    Coin('TRU'),
    Coin('DENT'),
    Coin('HOT'),
    Coin('VTHO'),
    Coin('MTL'),
    Coin('NKN'),
    Coin('RLC'),
    Coin('POLY'),
    Coin('DIA'),
    Coin('BEL'),
    Coin('PSG'),
    Coin('JUV'),
    Coin('CITY'),
    Coin('ATM'),
    Coin('ASR'),
]


exchange_bitget = Exchange('bitget')
exchange_bybit = Exchange('bybit')
exchange_gate = Exchange('gate')
exchange_kucoin = Exchange('kucoin')
exchange_okx = Exchange('okx')


exchange_bitget.coins = coin_list
exchange_bybit.coins = coin_list
exchange_gate.coins = coin_list
exchange_kucoin.coins = coin_list
exchange_okx.coins = coin_list

scout_bitget: ScoutBitget = ScoutBitget(exchange_bitget)
scout_bybit: ScoutBybit = ScoutBybit(exchange_bybit)
scout_gate: ScoutGate = ScoutGate(exchange_gate)
scout_kucoin: ScoutKucoin = ScoutKucoin(exchange_kucoin)
scout_okx: ScoutOkx = ScoutOkx(exchange_okx)


scouts_list: list[tuple[Exchange, Scout]] = [
    (exchange_bitget, scout_bitget),
    (exchange_bybit, scout_bybit),
    (exchange_gate, scout_gate),
    (exchange_kucoin, scout_kucoin),
    (exchange_okx, scout_okx)
]


sell_commission: dict[Coin, dict[Exchange, float]] = {
    coin: {
        exchange: 0 for exchange in Exchange.get_all()
    } for coin in coin_list
}

buy_commission:  dict[Coin, dict[Exchange, float]] = {
    coin: {
        exchange: 0 for exchange in Exchange.get_all()
    } for coin in coin_list
}

transfer_commission: dict[Coin, dict[Exchange, dict[Exchange, float]]] = {
    coin: {
        exchange_from: {
            exchange_to: 1.0 for exchange_to in Exchange.get_all() if exchange_to != exchange_from
        } for exchange_from in Exchange.get_all()
    } for coin in coin_list
}

transfer_time: dict[Coin, dict[Exchange, dict[Exchange, float]]] = {
    coin: {
        exchange_from: {
            exchange_to: 1.0 for exchange_to in Exchange.get_all() if exchange_to != exchange_from
        } for exchange_from in Exchange.get_all()
    } for coin in coin_list
}

guide = Guide(sell_commission=sell_commission, buy_commission=buy_commission, 
            transfer_commission=transfer_commission, transfer_time=transfer_time)
