from base_data import Data
from grid_info import GridInfo
import pandas as pd

class GridData(Data,GridInfo):
    def __init__(self,info=None,**kwargs):
        Data.__init__(self)
        GridInfo.__init__(self)  
        self._data = {}

    def to_df(self,var_name):
        pass

    def get_values_region(self,ranges=None):
        """
        Return a list of tuples of values at each grid point within the specified region
        
        Variables:
        - ranges: Dict which specifies the ranges in each dim
          e.g. {'lons':[0,100], 'lats':[0,60]}

        """
        if not ranges:
            values = {key: self._data[key].flatten() for key in self._data}
            return pd.DataFrame(values,columns=self._data.keys())
        for key in ranges:
            print(key)
            print(self._grid[key])

