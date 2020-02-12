from grid_data import GridData
from grads_wrapper import GradsWrapper
from analysis_utils import draw_progress_bar, ga_open_file, ga_read_ctl, ax_set

import matplotlib.pyplot as plt 
import matplotlib.colors as mcolors
import pandas as pd
import numpy as np
import datetime 
import os
import sys

class ModelZonalData(GridData):
    def __init__(self):
        GridData.__init__(self)
        self._axis_names = ['Height','Latitude']
    
    def read_grads_zonal(self,grads_dir,grads_names,
                      time_ranges=[1,1],file_suffixes=None,
                      zrange=None,check='check',show_progress=True,**kwargs):

        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        if type(zrange) != list: zrange = [1,1]
        ga = GradsWrapper(print=False)

        # Read latitude & height info
        lats, _, zlevs = ga_read_ctl(ga,grads_dir,grads_names[0],check,0,file_suffixes,time_ranges)
        
        self.set_grid('lats',lats)

        # # Get height
        if zrange[1] == zrange[0]:
            self.set_grid('zlevs',zlevs[0])
        else:
            self.set_grid('zlevs',zlevs[zrange[0]:zrange[1]+1])

        # Read data
        ttotal = sum(t[1]-t[0]+1 for t in time_ranges)
        data_num = len(time_ranges)*len(grads_names)*self._dims['zlevs']
        
        processed = 0
        all_data = self._data

        for grads_name in grads_names:
            data = np.zeros((self._dims['zlevs'],self._dims['lats'])) 
            for i in range(len(time_ranges)):
                trange = time_ranges[i]
                ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges)

                for i,z in enumerate(range(zrange[0],zrange[1]+1)):
                    ga.zlevel(z)
                    data[i] += np.nanmean(ga.tave_exp(grads_name,[1,2],**kwargs),axis=1)*(trange[1]-trange[0]+1)/ttotal
            
                    processed+=1
                    # if show_progress: 
                    #     draw_progress_bar(processed/data_num,show_progress)
                    # else:
                    print(f'Finished reading {processed}/{data_num}')
                    sys.stdout.flush()
                    
                ga.close()
            all_data[grads_name]= data

        self._data = all_data
        return 

    def plot_vertical_meridional(self,key,bounds=None,cmap='Reds',title=None,ax=None,key2=None,**kwargs):

        norm = mcolors.BoundaryNorm(bounds, ncolors=256) if bounds else None

        if not ax: fig, ax = plt.subplots()
        data = self._data[key]
        if key2: data = self._data[key2]-data
        pcm=ax.pcolormesh(self._grid['lats'],self._grid['zlevs']/1000,data,cmap=cmap,norm=norm)

        ax_settings = {'xlabel': 'Latitude',
                       'ylabel': 'Height (km)',
                       'title': title or  key,
                       'save_suffix':key}
        ax_set(ax,**ax_settings,**kwargs)

        plt.colorbar(pcm,ax=ax)


        