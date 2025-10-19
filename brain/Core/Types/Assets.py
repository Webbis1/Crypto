from dataclasses import dataclass
from .Coin2 import Coin


@dataclass
class Assets:
    currency: Coin
    amount: float