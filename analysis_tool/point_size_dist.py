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
        self._bin_centers = {key:self._info[key]['data'].get_bin_centers() for key in self._keys}
        self._bin_num = {key:self._info[key]['data'].get_bin_num() for key in self._keys} 
        self._size_col = {key: ['{}.{}'.format(self._info[key]['prefix'],i+1) for i in range(self._bin_num[key])] for key in self._keys}
    def get_bin_centers(self):
        return self._bin_centers

    def plot_size_dist(self,
                    sites=['SEDE_BOKER'],prefix='prefix',
                    xscale='log',
                    xlabel='Diameter (${\mu}$m)',
                    ylabel='dV/dlnr',**kwargs):

        if not sites: sites = self._groupnames
        ax_settings = {'xscale': xscale, 'xlabel':xlabel,'ylabel':ylabel}

        for i,site in enumerate(sites):
            fig,ax = plt.subplots()
            for key in self._keys:
                centers = self._bin_centers[key]
                counts = len(self._groupbys[key].get_group(site))
                data =  list(self._groupbys[key].get_group(site).mean()[self._size_col[key]])
                ax.plot(centers,data,label=key,**self._styles[key])

            ax_settings['title'] = f'{site}: (N={counts})'
            ax_settings['save_suffix'] = site
            ax_set(ax,**ax_settings,**kwargs)






        