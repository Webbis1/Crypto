from .Types import *
from .Analyst import Analyst
from .Guide import Guide


exchange_list: list[Exchange] = [Exchange('bitget'), Exchange('kucoin'), Exchange('gate'), Exchange('bybit')]


scout_head: ScoutHead = ScoutHead()
guide: Guide = Guide()

analyst: Analyst = Analyst(scout_head, guide)


