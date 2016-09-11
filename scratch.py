"""
* Got a dataset that's too large to load in a single chunk
* So need to chunk the date range
* Then process each chunk independently
* Then nail the results back together

* Need support for both explicit dependency listings and dependency discovery
    * Explicit listings can be done with a decorator, mapping world.x to dicts of extra arguments
#    * Dependency discovery should
"""
import scipy as sp
import pandas as pd
from distributed import Executor

class World(object):

    def __init__(self, start, end):
        self._start = start
        self._end = end
    
    def get_data(self):
        sp.random.seed(591989)
        dates = pd.date_range('2000', '2017', freq='D')
        data = pd.Series(sp.random.normal(size=len(dates)), dates)
        return data.loc[self._start:self._end]

def get_chunks(start, end, count, warmup=7):
    dates = pd.date_range(pd.to_datetime(start), end)
    size = len(dates)//count
    chunks = [(dates[i], dates[min(i+warmup+size, len(dates)-1)]) 
                    for i in range(0, len(dates), size)]
    return chunks

def f(w):
    data = w.get_data()
    return data.ewm(halflife=30).mean()

def run():
    start, end = '2000', '2016'
    count = 20
    warmup = 90
    
    client = Executor('192.168.1.27:8786')
    
    results = []
    for s, e in get_chunks(start, end, count, warmup):
        w = World(s, e)
        result = client.submit(f, w)
        results.append(result)
    
    results = [r.result() for r in results]