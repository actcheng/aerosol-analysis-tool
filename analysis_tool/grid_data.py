from base_data import Data
from grid_info import GridInfo

class GridData(Data,GridInfo):
    def __init__(self,info=None,**kwargs):
        Data.__init__(self)
        GridInfo.__init__(self)  
        self._data = {}

    def to_df(self,var_name):
        pass

