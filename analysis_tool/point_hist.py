from analysis_utils import ax_selector,get_freq, ax_set
from group_data import GroupData

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

class PointHist(GroupData):
    def __init__(self,info=None,**kwargs):
        GroupData.__init__(self,info)

    def plot_frequency(self,param,bins,xscale='log',ylabel='Relative frequency',**kwargs): 
        """ Plot histogram based on the given parameter as passed in the info"""
        axes = []
        ax_settings = {'xscale': xscale, 'ylabel':ylabel }

        centers = [(bins[i]+bins[i+1])*0.5 for i in range(len(bins)-1)]
        for i, groupname in enumerate(self._groupnames):
            fig,ax = plt.subplots()    
            for key in self._keys:
                try:
                    data = self._groupbys[key].get_group(groupname)[self._info[key][param]]

                    ax.plot(centers,get_freq(data,bins=bins),**self._styles[key],label=key)
                except:
                    print(f'Not plotted for {key} at {groupname}')
            ax_settings['title'] = groupname
            ax_settings['save_suffix'] = groupname

            ax_set(ax,**ax_settings,**kwargs)
            
            axes.append(ax)

        return axes