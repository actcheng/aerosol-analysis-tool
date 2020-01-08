from analysis_utils import ax_selector,get_freq, ax_set
from base_data import Data

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

'''''
Example input:

info = {'GAW':{'data': gaw, (PointData)
                 'num_conc':'particle_number_concentration',
                 'style': {'linewidth': 3,
                           'linecolor': 'k'}
                },
           'Model':{'data': model,
                 'num_conc':'N_sfc',
                 'style': {'linewidth': 1,
                           'color': 'red'}
            }}
          
'''''

class PointHist(Data):
    def __init__(self,info=None,**kwargs):
        Data.__init__(self)
        if info: self.set_info(info,**kwargs)
            

    def set_info(self,info,by='Site name'):
        self._info = info
        self._keys = list(info.keys())
        self._groupbys = {key:info[key]['data'].get_all_data().groupby(by)
                            for key in self._keys}
        self._groupnames = list(self._groupbys[self._keys[0]].groups.keys())
        self._styles = {key:info[key]['style'] for key in self._keys}

    def get_info(self):
        return self._info

    def get_keys(self):
        return self._keys
    
    def get_groupbys(self):
        return self._groupbys

    def get_groupnames(self):
        return self._groupnames

    def get_styles(self):
        return self._styles

    def set_styles(self,key,param,value):
        self._style[key][param] = value


    def plot_frequency(self,param,bins,xscale='log',save_prefix=None,**kwargs): 
        """ Plot histogram based on the given parameter as passed in the info"""
        axes = []
        ax_settings = {'xscale': xscale }

        centers = [(bins[i]+bins[i+1])*0.5 for i in range(len(bins)-1)]
        for i, groupname in enumerate(self._groupnames[:1]):
            fig,ax = plt.subplots()    
            for key in self._keys:
                data = self._groupbys[key].get_group(groupname)[self._info[key][param]]

                ax.plot(centers,get_freq(data,bins=bins),**self._styles[key],label=key)

            ax_settings['title'] = groupname
            if save_prefix: ax_settings['savename'] = f'{save_prefix}_{groupname.lower()}'
            ax_set(ax,**ax_settings,**kwargs)
            
            axes.append(ax)

        return axes