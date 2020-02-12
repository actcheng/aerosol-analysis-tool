import pandas as pd
import numpy as np

class GridInfo():

    def __init__(self):
        self._grid = {x:np.array([0,0]) for x in ['lats','lons','zlevs','time']}
        self._dims = {x:len(self._grid[x]) for x in self._grid}
        self._data = None
        self._axis_names = []

    def get_grid(self,dim):
        return self._grid[dim]

    def get_dims(self,dim):
        return self._dims[dim]

    def set_grid(self,dim,values):
        self._grid[dim] = np.array(values)
        self._dims[dim] = len(values)

    def get_axis_names(self):
        return self._axis_names

    def get_data(self):
        return self._data