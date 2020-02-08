from base_data import Data

import matplotlib.pyplot as plt
import numpy as np

class ZonalData(Data):
    def __init__(self):
        Data.__init__(self)
        self._lats = np.array([0,0])
        self._nlat = len(self._lats)
        self._zlevs = np.array([0]) 
        self._nz = len(self._zlevs)
        self._data = {}
        
    def get_nlat(self):
        return self._nlat

    def set_lats(self,lats):
        self._lats = np.array(lats)
        self._nlat = len(self._lats)

    def get_zlevs(self):
        return self._zlevs

    def get_nz(self):
        return self._nz

    def set_zlevs(self,zlevs):
        self._zlevs = np.array(zlevs)
        self._nz = len(self._zlevs)

    def get_data(self):
        return self._data