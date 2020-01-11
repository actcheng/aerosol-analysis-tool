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
        GroupData.__init__(self,info=info,**kwargs)
        
    def set_info(self,info,by='Site name'):
        super().set_info(info,by)
        # self._bin_centers = {key: self.pick_bin_centers(key)                                
        #                          for key in self._keys 
        #                          }
        self._bin_num = {key: self.pick_bin_num(key) for key in self._keys} 
        self._size_col = {key: ['{}.{}'.format(self._info[key]['prefix'],i+1) for i in range(self._bin_num[key])] for key in self._keys}

    def pick_bin_centers(self,key,group=None):
        if ('centers' not in self._info[key]) or (self._info[key]['centers'] == 'default'):
            return self._info[key]['data'].get_bin_centers()  
        elif self._info[key]['centers'] == 'fixed':
            return self._info[key]['data'].get_type_info()[key].get_bin_centers() 
        else:
            columns=self._info[key]['data'].get_type_info()[key].get_centerlist()
            return list(group.mean()[columns])

    def pick_bin_num(self,key):
        if ('centers' not in self._info[key]) or (self._info[key]['centers'] == 'default'):
            return self._info[key]['data'].get_bin_num() 
        else: 
            return self._info[key]['data'].get_type_info()[key].get_bin_num()

    def get_bin_centers(self):
        return self._bin_centers

    def plot_size_dist(self,
                    sites=[],prefix='prefix',
                    xscale='log',
                    xlabel='Diameter (${\mu}$m)',
                    ylabel='dV/dlnr',
                    count_key='',
                    close=False,
                    **kwargs):

        if len(sites)==0: sites = self._groupnames
        ax_settings = {'xscale': xscale, 'xlabel':xlabel,'ylabel':ylabel}
        
        for i,site in enumerate(sites):
            counts = 0
            fig,ax = plt.subplots()
            for key in self._keys:
                
                group = self._groupbys[key].get_group(site).dropna(how='all')
                centers = self.pick_bin_centers(key,group)
                # (self._bin_centers[key] 
                #             if self._info[key]['centers'] == 'fixed'
                #             else list(group.mean()[self._bin_centers[key]]))

                if key == count_key: 
                    counts = len(group)
                data =  list(group.mean()[self._size_col[key]])
                ax.plot(centers,data,label=key,**self._styles[key])

            ax_settings['title'] = f'{site}: (N={counts})' if counts>0 else site
            ax_settings['save_suffix'] = site
            ax_set(ax,**ax_settings,**kwargs)
            if close: plt.close()






        