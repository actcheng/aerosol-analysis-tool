from grid_data import GridData
from grads_wrapper import GradsWrapper
from analysis_utils import draw_progress_bar, ga_open_file, ga_read_ctl, ax_set

import matplotlib.pyplot as plt 
import matplotlib.colors as mcolors
import matplotlib as mpl
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

import pandas as pd
import numpy as np
import datetime 
import os
import sys

class ModelGridData(GridData):
    def __init__(self):
        GridData.__init__(self)
        self._zlist = []

    def set_zlist(self,zlist):
        self._zlist = zlist
    
    def get_zid(self,z):
        return self._zlist.index(z)

    def get_zlist(self):
        return self._zlist

    def read_grads_grid_all(self,grads_dir,grads_names,
                            file_suffixes=None,
                            time_ranges=[1,1],
                            start_date=datetime.datetime(2006,1,1),
                            zlist=[1],check='check',
                            show_progress=True,**kwargs):

        if not self._axis_names: 
            self._axis_names = ['zlevs','lats','lons','time']
        else:
            if len(self._axis_names) != 4: 
                raise('Inconsistent dimensions with existing data!')

        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        if type(zlist) != list: zlist = [zlist]
        self.set_zlist(zlist)

        ga = GradsWrapper(print=False)

        # Read latitude & height info
        lats, lons, zlevs = ga_read_ctl(ga,grads_dir,grads_names[0],check,0,file_suffixes,time_ranges)
        
        self.set_grid('lats',lats)
        self.set_grid('lons',lons)
        self.set_grid('zlevs',zlevs)

        ttotal = sum(t[1]-t[0]+1 for t in time_ranges)
        times = [start_date]*ttotal
        for i in range(1,ttotal):
            times[i] = times[i-1]+datetime.timedelta(1)
        self.set_grid('time',times)

        # Read data
        data_num = len(time_ranges)*len(grads_names)*len(zlist)
        
        processed = 0
        all_data = self._data

        for grads_name in grads_names:
            data = []
            for i in range(len(time_ranges)):
                data_z = []
                trange = time_ranges[i]
                ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges)

                for i,z in enumerate(zlist):
                    ga.zlevel(z)
                    data_z.append(ga.tloop(grads_name,trange=trange,**kwargs))
            
                    processed+=1
                    if show_progress: 
                        draw_progress_bar(processed/data_num,show_progress)
                    else:
                        print(f'Finished reading {processed}/{data_num}')
                    sys.stdout.flush()
                    
                ga.close()
                data.append(np.stack(data_z))
            all_data[grads_name]= np.concatenate(data,axis=-1)

        self._data = all_data
        return 

    def read_grads_grid_avg(self,grads_dir,grads_names,
                            file_suffixes=None,
                            read_grid=True,
                            time_ranges=[1,1],
                            start_date=datetime.datetime(2006,1,1),
                            zlist=[1],check='check',
                            show_progress=True,**kwargs):

        if not self._axis_names: 
            self._axis_names = ['zlevs','lats','lons']
        else:
            if len(self._axis_names) != 3: 
                raise('Inconsistent dimensions with existing data!')

        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        if type(zlist) != list: zlist = [zlist]
        self.set_zlist(zlist)

        ga = GradsWrapper(print=False)

        if read_grid:
            # Read latitude & height info
            lats, lons, zlevs = ga_read_ctl(ga,grads_dir,grads_names[0],check,0,file_suffixes,time_ranges)
            
            self.set_grid('lats',lats)
            self.set_grid('lons',lons)
            self.set_grid('zlevs',zlevs)

        ttotal = sum(t[1]-t[0]+1 for t in time_ranges)

        if self._grid['time'][0] == 0:
            self.set_grid('time',[start_date])
        elif start_date not in self._grid['time']:
            self.set_grid('time',np.append(self._grid['time'],start_date))

        # Read data
        data_num = len(grads_names)*len(zlist)*len(time_ranges)
        
        processed = 0
        all_data = self._data

        for grads_name in grads_names:
            data = []
            for i in range(len(time_ranges)):
                trange = time_ranges[i]
                ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges)

                for i,z in enumerate(zlist):
                    ga.zlevel(z)
                    res = ga.tave_grid(grads_name,trange=trange,**kwargs) *(trange[1]-trange[0]+1)/ttotal
                    if i == len(data):
                        data.append(res)
                    else:
                        data[i] += res

                    processed+=1
                    if show_progress: 
                        draw_progress_bar(processed/data_num,show_progress)
                    else:
                        print(f'Finished reading {processed}/{data_num}')
                    sys.stdout.flush()
                    
                ga.close()

            if grads_name in all_data:
                all_data[grads_name] = np.vstack([all_data[grads_name],np.stack(data)])
            else:
                all_data[grads_name]= np.stack(data)

        self._data = all_data 

        return 

    def plot_grid(self,param,z=0,ax=None,bounds=None,cmap='Reds',colorbar=True,mask=None,key2=None,cax=None,**kwargs):
        
        projection = ccrs.PlateCarree()

        norm = mcolors.BoundaryNorm(bounds, ncolors=256) if bounds else None

        if not ax: fig, ax = plt.subplots(figsize=(10,4),subplot_kw={'projection': ccrs.PlateCarree()})
        
        x = self.get_grid('lons')
        y = self.get_grid('lats')
        data = self.get_data()[param][z]
        if key2:
            data = data-self.get_data()[key2][z]

        if type(mask) == np.ndarray: 
            data = np.ma.array(data, mask = mask)
            print(data.shape,mask.shape)       

        ax.coastlines()
        ax.set_xticks(np.linspace(-180, 180, 5), crs=projection)
        ax.set_yticks(np.linspace(-90, 90, 5), crs=projection)

        ax_settings = {
            'xlim': [-180,180],
            'ylim':[-90,90]
        }
        ax_set(ax,**ax_settings,**kwargs)

        pcm=ax.pcolormesh(x,y,data,cmap=cmap,norm=norm)

        if colorbar: 
            cb = plt.colorbar(pcm,ax=ax,extend='max')
           

        return ax

    def plot_histogram(self,param,bins, zlist=1,
                       styles={},
                       xscale='linear',
                       yscale='linear', ylabel='Relative frequency',
                       ax=None,**kwargs):

        ax_settings = {'xscale': xscale, 
                       'yscale': yscale, 'ylabel':ylabel,
                       'save_suffix': param }
        
        if type(zlist) != list: zlist = [zlist]
        if not ax: fig, ax = plt.subplots()
        centers = [(bins[i+1]+bins[i])/2 for i in range(len(bins)-1)]
        
        for z in zlist:
            h = self._grid['zlevs'][z-1]
            data = self.get_data()[param][self.get_zid(z)].flatten()
            counts, _ = np.histogram(data,bins=bins,density=True)
            ax.plot(centers,counts,label=f'{int(h/10)/100} km',**styles)

        print('Total counts: ',len(data))

        ax_set(ax,**ax_settings,**kwargs)

        return
            
    