from sortedcontainers import ValueSortedDict
from datetime import datetime


d = {'a': {'datetime': datetime.datetime.now()}, 'b': {'datetime': datetime.datetime.now()}, 'z': {'datetime': datetime.datetime.now()}, 'c': {'datetime': datetime.datetime.now()}}
vsd = ValueSortedDict()
for k, v in d.items():                                                                                                                                              
    vsd[k] = v['datetime']
vsd['d'] = datetime.datetime.now()