from dataclasses import dataclass
from .Coin import Coin


@dataclass
class Assets:
    currency: Coin
    amount: float