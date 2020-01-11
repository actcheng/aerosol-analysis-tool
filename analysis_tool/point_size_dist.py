from analysis_utils import ax_selector, ax_set
from group_data import GroupData

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

'''''
Example input:

info = {'AERONET':{'data': gaw, (PointData)
                 'prefix':'pdvdlnr',
                 'style': {'linewidth': 3,
                           'color': 'k'}
                },
           'Sulfate':{'data': model,
                 'prefix':'N_sfc',
                 'style': {'linewidth': 1,
                           'color': 'red'}
            }}
          
'''''

class PointSizeDist(GroupData):
    def __init__(self,info=None,**kwargs):
        GroupData.__init__(self,info=info)
        
    def set_info(self,info,by='Site name'):
        super().set_info(info,by)
        self._bin_centers = {key:self._info[key]['data'].get_bin_centers() 
                                 if 'total' in self._info[key] and self._info[key]['total']
                                 else self._info[key]['data'].get_type_info()[key].get_bin_centers()
                                 for key in self._keys 
                                 }
        self._bin_num = {key:self._info[key]['data'].get_bin_num()
                            if 'total' in self._info[key] and self._info[key]['total']
                            else self._info[key]['data'].get_type_info()[key].get_bin_num()
                            for key in self._keys} 
        self._size_col = {key: ['{}.{}'.format(self._info[key]['prefix'],i+1) for i in range(self._bin_num[key])] for key in self._keys}

    def get_bin_centers(self):
        return self._bin_centers

    def plot_size_dist(self,
                    sites=[],prefix='prefix',
                    xscale='log',
                    xlabel='Diameter (${\mu}$m)',
                    ylabel='dV/dlnr',
                    count_key='',
                    **kwargs):

        if len(sites)==0: sites = self._groupnames
        ax_settings = {'xscale': xscale, 'xlabel':xlabel,'ylabel':ylabel}
        
        for i,site in enumerate(sites):
            counts = 0
            fig,ax = plt.subplots()
            for key in self._keys:
                centers = self._bin_centers[key]
                group = self._groupbys[key].get_group(site).dropna(how='all')
                if key == count_key: 
                    counts = len(group)
                data =  list(group.mean()[self._size_col[key]])
                ax.plot(centers,data,label=key,**self._styles[key])

            ax_settings['title'] = f'{site}: (N={counts})' if counts>0 else site
            ax_settings['save_suffix'] = site
            ax_set(ax,**ax_settings,**kwargs)
            plt.close()






        