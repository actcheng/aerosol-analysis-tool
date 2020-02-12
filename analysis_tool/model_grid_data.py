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

class ModelGridData(GridData):
    def __init__(self):
        GridData.__init__(self)

    def read_grads_grid_all(self,grads_dir,grads_names,
                            file_suffixes=None,
                            time_ranges=[1,1],
                            start_date=datetime.datetime(2006,1,1),
                            zrange=None,check='check',
                            show_progress=True,**kwargs):

        if not self._axis_names: 
            self._axis_names = ['zlevs','lats','lons','time']
        else:
            if len(self._axis_names) != 4: 
                raise('Inconsistent dimensions with existing data!')

        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        if type(zrange) != list: zrange = [1,1]
        ga = GradsWrapper(print=False)

        # Read latitude & height info
        lats, lons, zlevs = ga_read_ctl(ga,grads_dir,grads_names[0],check,0,file_suffixes,time_ranges)
        
        self.set_grid('lats',lats)
        self.set_grid('lons',lons)

        if zrange[1] == zrange[0]:
            self.set_grid('zlevs',zlevs[0])
        else:
            self.set_grid('zlevs',zlevs[zrange[0]:zrange[1]+1])

        ttotal = sum(t[1]-t[0]+1 for t in time_ranges)
        times = [start_date]*ttotal
        for i in range(1,ttotal):
            times[i] = times[i-1]+datetime.timedelta(1)
        self.set_grid('time',times)

        # Read data
        data_num = len(time_ranges)*len(grads_names)*self._dims['zlevs']
        
        processed = 0
        all_data = self._data

        for grads_name in grads_names:
            data = []
            for i in range(len(time_ranges)):
                data_z = []
                trange = time_ranges[i]
                ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges)

                for i,z in enumerate(range(zrange[0],zrange[1]+1)):
                    ga.zlevel(z)
                    data_z.append(ga.tloop(grads_name,trange=trange,**kwargs))
            
                    processed+=1
                    # if show_progress: 
                    #     draw_progress_bar(processed/data_num,show_progress)
                    # else:
                    print(f'Finished reading {processed}/{data_num}')
                    sys.stdout.flush()
                    
                ga.close()
                data.append(np.stack(data_z))
            all_data[grads_name]= np.stack(data,axis=-1)

        self._data = all_data
        return 

    def plot_histogram(self,param,bins, zlist=1,
                       histtype='step', 
                       xscale='linear',
                       yscale='log', ylabel='Frequency',
                       ax=None,**kwargs):

        ax_settings = {'xscale': xscale, 
                       'yscale': yscale, 'ylabel':ylabel,
                       'save_suffix': param }
        
        if type(zlist) != list: zlist = [zlist]
        if not ax: fig, ax = plt.subplots()

        for z in zlist:
            h = self._grid['zlevs'][z-1]
            data = self.get_data()[param][z-1].flatten()
            ax.hist(data,bins=bins,histtype=histtype,label=f'{int(h)} m')

        if len(zlist) > 1: ax.legend()

        ax_set(ax,**ax_settings,**kwargs)

        return
            



