from model_grid_data import ModelGridData
import pandas as pd
import numpy as np
import datetime 
import os
import sys

class ModelGridDataCompare():

    def __init__(self,base_data,compare_data):
        self.data = {'Base': base_data, 'Compare': compare_data}

    # Functions
    # Mean (Any functions indeed)
    # Histogram of all points (daily / monthly avg / annual avg)
    # Diff plot (avg)
    def diff(self,key,selections={},**kwargs):
        data = {case: np.squeeze(self.data[case].axis_avg(keys=[key],
                                 selections=selections).sum(axis=0))
                for case in self.data
        }
        return   data['Compare'] - data['Base']
        # diff = {key: data['Base'] - data['Compare']}
        # grid_data = ModelGridData()
        # grid_data.set_data(diff)
        # grid_data.set_grid('lats',self.data['Base'].get_grid('lats'))
        # grid_data.set_grid('lons',self.data['Base'].get_grid('lons'))

        # return grid_data

    # def plot_diff(self,key)
