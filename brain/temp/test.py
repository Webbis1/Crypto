import ccxt.pro as ccxtpro
from asyncio import run
import asyncio
from pprint import pprint
import signal

async def main():
    exchange = ccxtpro.kraken({'newUpdates': False})
    while True:
        orderbook = await exchange.watch_order_book('BTC/USD')
        print(orderbook['asks'][0], orderbook['bids'][0])
    await exchange.close()


# run(main())

async def watchOrderBook(exchange, symbol, limit=10, params={}):
    if exchange.has['watchOrderBookForSymbols']:
        while True:
            try:
                tickers = await exchange.watch_tickers(['BTC/USDT', 'ETH/USDT'], params)
                print(exchange.iso8601(exchange.milliseconds()), tickers)
            except Exception as e:
                print(e)
                # stop the loop on exception or leave it commented to retry
                # raise e


async def main():
    kraken = ccxtpro.kraken({'newUpdates': True})
    bitget = ccxtpro.bitget()
    try:
        await watchOrderBook(bitget, 'BTC/USDT')
    except asyncio.CancelledError:
        print("\nGracefully shutting down...")
    finally:
        await bitget.close()

run(main())


# def shutdown(loop):
#     for task in asyncio.all_tasks(loop):
#         task.cancel()

# loop = asyncio.get_event_loop()
# for sig in (signal.SIGINT, signal.SIGTERM):
#     loop.add_signal_handler(sig, lambda: shutdown(loop))

# try:
#     loop.run_until_complete(main())
# finally:
#     loop.close()
    


# kraken = ccxtpro.kraken({'newUpdates': True})
# if (kraken.has['watchTicker']):
#     pprint(kraken.options['watchTicker']['name'])
# else:
#     print('no have watchticker')


async def test(symbol = 'BTC/USDT'):
    # Python
    exchange = ccxtpro.binance()
    if exchange.has['watchOHLCV']:
        while True:
            try:
                ohlcv = await exchange.watch_ohlcv(symbol, timeframe='1s')
                for candle in ohlcv:
                    timestamp, open_price, high_price, low_price, close_price, volume = candle
                    print(f"Timestamp: {timestamp}, Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}, Volume: {volume}")
            except Exception as e:
                print(f"Error while fetching OHLCV data: {e}")
                # stop the loop on exception or leave it commented to retry
                # raise e
    else:
        print(f"{exchange.id} does not support watchOHLCV")


# run(test())