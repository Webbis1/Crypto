from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

@dataclass
class TickerData:
    symbol: str
    exchange: str
    bid: Optional[float] = None
    ask: Optional[float] = None
    last: Optional[float] = None
    volume: Optional[float] = None
    timestamp: float = 0.0
    spread: float = 0.0
    spread_percent: float = 0.0
    
    def __post_init__(self) -> None:
        if (self.bid is not None) and (self.ask is not None):
            try:
                self.spread = float(self.ask) - float(self.bid)
                self.spread_percent = (self.spread / float(self.bid)) * 100 if float(self.bid) != 0 else 0.0
            except Exception:
                self.spread = 0.0
                self.spread_percent = 0.0