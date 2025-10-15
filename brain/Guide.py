from dataclasses import dataclass
from typing import Dict
from Types import Coin, Exchange


@dataclass
class Guide:
    sell_commission: Dict[Coin, Dict[Exchange, float]]
    buy_commission: Dict[Coin, Dict[Exchange, float]] 
    transfer_commission: Dict[Coin, Dict[Exchange, Dict[Exchange, float]]]
    transfer_time: Dict[Coin, Dict[Exchange, Dict[Exchange, float]]]
    min_amount: Dict[Coin, Dict[Exchange, float]]
    max_amount: Dict[Coin, Dict[Exchange, float]]
