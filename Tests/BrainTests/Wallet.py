from dataclasses import dataclass

@dataclass
class Exchange:
    coins: dict[int, float]

@dataclass
class Wallet:
    exchanges: dict[int, Exchange]
    
    

