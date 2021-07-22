from grid_data import GridData
from grads_wrapper import GradsWrapper
from analysis_utils import draw_progress_bar,ga_open_file, ga_read_ctl, ax_set,gammafunc

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
            print(grads_name)
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
                        # data[i] += res
                        data[i] = np.nansum([data[i],res],axis=0)
                        # print(data[i].shape,res.shape)

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

    def read_grads_aave(self,grads_dir,grads_names,
                    file_suffixes=None,
                  lons=[-180,180],lats=[-90,90],
                  time_ranges=[1,1],zlist=[1],
                  time=1,check='check',op='',
                  **kwargs): 
        
        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        if type(zlist) != list: zlist = [zlist]

        # op = '*{}*{}{}'.format(area,time,op)
        tint = [t[1]-t[0]+1 for t in time_ranges]
        ttotal = sum(tint)

        processed = 0
        data_num = len(grads_names)*len([t for t in time_ranges if 0 not in t])

        ga = GradsWrapper(print=False)
        data = {}
        for grads_name in grads_names:
            data[grads_name] = np.zeros((1,))
            for i,trange in enumerate(time_ranges):
                if 0 in trange: continue
                ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges)
                for j,z in enumerate(zlist):
                    ga.zlevel(z)      
                    data[grads_name][j] +=  ga.aave(grads_name,trange=trange,op=op,lons=lons,lats=lats,**kwargs) *tint[i]/ttotal
                    
                    processed += 1
                    draw_progress_bar(processed/data_num)

                ga.close()

        print(data)
            
        return data

    ### Read cloud-top values
    def read_cloud_top(self,grads_dir,grads_names,
                        qc_name = 'ms_qc',
                        thres=1e-5,
                        file_suffixes=None,
                        time_ranges=[1,1],
                        start_date=datetime.datetime(2006,1,1),
                        zrange=[1,40],check='check',
                        show_progress=True,**kwargs):

        """Read 3D var and get cloud-top values (2D) """
        if not self._axis_names: 
            self._axis_names = ['zlevs','lats','lons','time']
        else:
            if len(self._axis_names) != 4: 
                raise('Inconsistent dimensions with existing data!')

        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        self.set_zlist([1])

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
        data_num = len(time_ranges)*len(grads_names)*(zrange[1]-zrange[0]+1)
        
        processed = 0
        all_data = self._data
        data_2d = {}
        data = {}
        for i in range(len(time_ranges)):
            trange = time_ranges[i]
            for t in range(trange[0],trange[1]+1):
                data_3d = {}
                for grads_name in grads_names:
                    print(grads_name,t)
                    sys.stdout.flush()   
                    ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges)
                    ga.zlevel(zrange[0],zrange[1])
                    ga.time(t)
                    data_3d[grads_name] = ga.ga_exp(grads_name)
                    ga.close()
                print('get_cloud_top_index', t)
                sys.stdout.flush()   
                ind= get_cloud_top_index(data_3d[qc_name],thres)
                print('finished get_cloud_top_index')
                sys.stdout.flush()   
                for grads_name in grads_names:
                    if grads_name not in data_2d:
                        data_2d[grads_name] = [get_cloud_top_data(data_3d[grads_name],ind)]
                    else:
                        data_2d[grads_name].append(get_cloud_top_data(data_3d[grads_name],ind))
               
        for grads_name in grads_names:
            data_2d[grads_name] = np.expand_dims( np.moveaxis(np.stack(data_2d[grads_name]),0,2),0)

        self.set_data(data_2d)
        return data_2d

    # Cloud effective radius calcuation
    def calculate_rceff(self,rceff_name='rceff',
                        qc_name='ms_qc',unccn_name='unccn',
                        rho_name='ms_rho'):
        print('Calculate cloud effective radius')
        rho_w     = 1000.0

        qc = self._data[qc_name]
        unccn = self._data[unccn_name]
        rho = self._data[rho_name]

        qc = np.where(qc==0.0,np.nan,qc)
        Nc = unccn*1e-6
        dens = rho
        rhoqc = dens * qc * 1000.0
        # coef_dgam
        Dc         = 0.146 - 5.964E-2 * np.log( Nc / 2000.0 ) # Nc? Nc_def?
        dgamma_a   = 0.1444 / Dc**2
        GAM_dgam   = gammafunc( dgamma_a )
        GAM_dgam23 = gammafunc( dgamma_a + 2.0/3.0 )
        coef_dgam  = GAM_dgam23 / GAM_dgam * dgamma_a**(-2.0/3.0)
        # rf_qc & coef_xf for moments calculation
        xf_qc = rhoqc / Nc * 1.E-9
        coef_xf    = 3.0 / 4.0 / np.pi / rho_w
        rf_qc = ( coef_xf * xf_qc + 1.E-16 )**(1.0/3.0) 
        
        # Moments
        r2_qc = coef_dgam * rf_qc**2 * ( Nc * 1E+6 )
        r3_qc = coef_xf * dens * qc

        # Effective radius
        rceff = r3_qc / r2_qc

        self._data['rceff'] = rceff
        return rceff

    def get_histogram(self,param,bins,z=1,scale_factor=1):
        data = self.get_data()[param][self.get_zid(z)].flatten()
        data = data[~np.isnan(data)]*scale_factor
        print(param,np.log10(data.min()),np.log10(data.max()))
        counts, _ = np.histogram(data,bins=bins)
        return counts

    ### plot
    def plot_histogram(self,param,bins, zlist=1,
                       styles={},
                       xscale='linear',
                       yscale='linear', ylabel='Relative frequency',
                       ax=None,label=None,
                       scale_factor=1,
                       **kwargs):

        ax_settings = {'xscale': xscale, 
                       'yscale': yscale, 'ylabel':ylabel,
                       'save_suffix': param }
        
        if type(zlist) != list: zlist = [zlist]
        if not ax: fig, ax = plt.subplots()
        centers = [(bins[i+1]+bins[i])/2 for i in range(len(bins)-1)]
        for z in zlist:
            h = self._grid['zlevs'][z-1]
            data = self.get_data()[param][self.get_zid(z)].flatten()
            data = data[~np.isnan(data)]*scale_factor
            print(param,np.log10(data.min()),np.log10(data.max()))
            counts, _ = np.histogram(data,bins=bins)
            print(counts)
            ax.plot(centers,counts,label=label or f'{int(h/10)/100} km',**styles)
        
        print('Total counts: ',len(data))

        ax_set(ax,**ax_settings,**kwargs)

        return
            
####### Utils
def get_cloud_top_index(data,thres):
    nlat, nlon, nz = data.shape
    print(nlat,nlon,nz)
    def find_max_ind_thres(a):
        for i in range(nz-1,3,-1):
            if a[i] > thres: return i
        return 0
        
    res = np.apply_along_axis(find_max_ind_thres,2,data)
    print(res.max())
    return res

def get_cloud_top_data(data,ind):    
    return np.apply_along_axis(lambda a: a[int(a[-1])], 2,
                             np.concatenate((data,
                                             np.expand_dims(ind,2)),
                                             axis=2))

