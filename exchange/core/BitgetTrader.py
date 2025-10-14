from .Types import Trader, Assets, Destination
import ccxt
import asyncio
import socket
import json
from typing import Optional, Dict, Any


class BitgetTrader(Trader):
    def __init__(self, api_key: str, secret: str, password: str):
        self.exchange = ccxt.bitget({
            'apiKey': api_key,
            'secret': secret,
            'password': password,
            'sandbox': False,
            'options': {
                'createMarketBuyOrderRequiresPrice': False
            }
        })

    async def trade(self, selling: Assets, buying: str) -> Optional[Dict[str, Any]]:
        if not selling or not selling.currency or selling.amount <= 0:
            print(f"❌ Invalid selling asset: {selling}")
            return None
        if not buying or not isinstance(buying, str):
            print(f"❌ Invalid buying currency: {buying}")
            return None

        loop = asyncio.get_running_loop()

        try:
            await loop.run_in_executor(None, self.exchange.load_markets)
            print(f"✅ Markets loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load markets: {e}")
            return None

        # Determine trading direction
        if buying.upper() == 'USDT':
            # Selling crypto for USDT
            symbol = f"{selling.currency.upper()}/USDT"
            side = 'sell'
            amount = selling.amount
            print(f"🔄 Selling {amount} {selling.currency} for USDT")
            
        elif selling.currency.upper() == 'USDT':
            # Buying crypto with USDT (market buy)
            symbol = f"{buying.upper()}/USDT" 
            side = 'buy'
            cost = selling.amount  # Amount of USDT to spend
            print(f"🔄 Buying {buying} with {cost} USDT")
            
        else:
            # Trading between two non-USDT currencies
            symbol = f"{selling.currency.upper()}/{buying.upper()}"
            side = 'sell'
            amount = selling.amount
            print(f"🔄 Trading {amount} {selling.currency} for {buying}")

        if symbol not in self.exchange.symbols:
            print(f"❌ Trading pair not found: {symbol}")
            return None

        print(f"🎯 Creating market {side} order for {symbol}")

        try:
            if side == 'buy' and selling.currency.upper() == 'USDT':
                # For market buy orders with USDT
                order = await loop.run_in_executor(
                    None,
                    lambda: self.exchange.create_order(symbol, 'market', side, None, None, {'cost': selling.amount})
                )
            else:
                # For sell orders or non-USDT buys
                order = await loop.run_in_executor(
                    None,
                    lambda: self.exchange.create_order(symbol, 'market', side, amount)
                )
            
            # Print the raw order response for debugging
            # print(f"📋 Raw order response: {json.dumps(order, indent=2, default=str)}")
            
            # Extract and display meaningful information
            order_id = order.get('id', 'Unknown')
            status = order.get('status', 'Unknown')
            
            print(f"✅ Order created successfully: {order_id}")
            print(f"📊 Status: {status}")
            
            # Try to get more details by fetching the order
            try:
                order_details = await loop.run_in_executor(
                    None,
                    lambda: self.exchange.fetch_order(order_id, symbol)
                )
                # print(f"📦 Fetched order details:")
                # print(f"   - Side: {order_details.get('side', 'Unknown')}")
                # print(f"   - Amount: {order_details.get('amount', 'Unknown')}")
                # print(f"   - Filled: {order_details.get('filled', 'Unknown')}")
                # print(f"   - Remaining: {order_details.get('remaining', 'Unknown')}")
                # print(f"   - Average Price: {order_details.get('average', 'Unknown')}")
                # print(f"   - Cost: {order_details.get('cost', 'Unknown')}")
                
                # Update the order with fetched details
                order.update(order_details)
                
            except Exception as fetch_error:
                print(f"⚠️ Could not fetch order details: {fetch_error}")
                # Still return the original order even if fetch fails
                
            return order
            
        except Exception as e:
            print(f"❌ Failed to create order: {e}")
            return None