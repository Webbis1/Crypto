# from sortedcontainers import ValueSortedDict
# from datetime import datetime


# d = {'a': {'datetime': datetime.datetime.now()}, 'b': {'datetime': datetime.datetime.now()}, 'z': {'datetime': datetime.datetime.now()}, 'c': {'datetime': datetime.datetime.now()}}
# vsd = ValueSortedDict()
# for k, v in d.items():                                                                                                                                              
#     vsd[k] = v['datetime']
# vsd['d'] = datetime.datetime.now()


from typing import Union


class Coin:
    def __init__(self, id: int, name: str):
        self.id = id
        self.name = name
    
    def __int__(self) -> int:
        return self.id

    def __str__(self) -> str:
        return self.name    
    


def print_id(id: Union[int]):
    print(id)
    
    
coin: Coin = Coin(5, "sdfsa")

print_id(coin)