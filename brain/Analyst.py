from .Types import Assets, ScoutHead
from typing import Dict, Optional, Any, AsyncIterator, List


class Analyst:
    matrix = []
    def __init__(self, scout: ScoutHead):
        self.scout = scout
    
    async def __aenter__(self):
        self.scout.coin_list()
        return self