from base_data import Data
from grid_info import GridInfo
from point_data import PointData
from analysis_utils import bound_to_index, lon360, lon180, ax_set,search_index
import pandas as pd
import numpy as np
import collections

import matplotlib.pyplot as plt 
import matplotlib.colors as mcolors
import matplotlib as mpl
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

class GridData(Data,GridInfo):
    def __init__(self,info=None,**kwargs):
        Data.__init__(self)
        GridInfo.__init__(self)  
        self._data = {}

    def axis_avg(self,axes_names=['time'],mask=None,keys=None,selections={}):
        res = {}
        if not keys: keys=self._data.keys()

        for key in keys:
            avg=np.ma.array(self._data[key].copy(), mask=mask)
            
            for axis in selections:
                axis_ind = self._axis_names.index(axis)

                if 'indices' in selections[axis]:
                    indices = selections[axis]['indices']
                elif 'values' in selections[axis]:
                    indices = [self._grid[axis].searchsorted(ind) for ind in selections[axis]['values']]
                avg = np.take(avg,indices,axis=axis_ind)
            
            for axis in axes_names:
                axis_ind = self._axis_names.index(axis)
                avg = np.nanmean(avg,axis=axis_ind,keepdims=True)
            res[key] = avg
        
        return res[keys[0]] if len(keys) == 1 else res

    def map_grid(self,grid_in,grid_name):
        return np.array([search_index(self.get_grid(grid_name),grid) for grid in grid_in])
        
    def create_mask(self,param,mappers,**kwargs):
        # mappers: array of mapper of each axis

        data = np.squeeze(self.axis_avg(keys=[param],**kwargs))

        mapped_ind = lambda mapper: lambda ind: mapper[ind]
        def f(*args):
            return np.isnan(data[tuple([mapped_ind(mappers[i])(arg) for i,arg in enumerate(args)])])

        dims = [len(mapper) for mapper in mappers]
        mask = np.fromfunction(f,dims,dtype=int)

        return mask

    def plot_grid(self,param=None,data=None,selections={},ax=None,cbounds=None,cmap='Reds',colorbar=True,mask=None,key2=None,cax=None,**kwargs):

        projection = ccrs.PlateCarree()

        norm = mcolors.BoundaryNorm(cbounds, ncolors=256) if cbounds else None

        if ax==None: fig, ax = plt.subplots(figsize=(10,4),subplot_kw={'projection': ccrs.PlateCarree()})
        x = self.get_grid('lons')
        y = self.get_grid('lats')
        if not data:        
            
            data = self.axis_avg(axes_names=[axis 
                                            for axis in self._axis_names 
                                            if axis not in ['lats','lons']],
                                            selections=selections,
                                            keys=[param],
                                  mask=mask)
        data = np.squeeze(data)   

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

    def plot_mean1d(self,param='aod',axis_name='lats',ax=None,label=None,selections={},color='k',**kwargs):
        axes_names = [name for name in self._axis_names if name != axis_name]
        data = np.squeeze(self.axis_avg(keys=[param],axes_names=axes_names,selections=selections))

        if not ax: fig, ax = plt.subplots()

        ax.plot(self._grid[axis_name],data,label=label,color=color)
        ax_set(ax,**kwargs)

    def plot_scatter_color(self,xname,yname,cname,cdata=None,region_ranges=None,ax=None,vmax=None,vmin=None,norm=None,cmap='gist_rainbow',s=4,colorbar=False,clabel=None,**kwargs):

        if not ax: fig, ax = plt.subplots()
        data = self.get_values_region(region_ranges=region_ranges,keys=[xname,yname,cname])
        
        if type(cdata) == type(None):
            cdata = data[cname]

        vmax = vmax or cdata.max()
        vmin = vmin or cdata.min()
        pcm = ax.scatter(data[xname],data[yname],c=cdata,vmin=vmin,vmax=vmax,cmap=cmap,s=s,norm=norm)

        ax_set(ax,legend=False,**kwargs)
        if colorbar: 
            cbar = plt.colorbar(pcm,ax=ax,extend='both')
            if clabel:cbar.set_label(clabel,rotation=270,labelpad=20)         


        return pcm

    def get_region_index_array(self,region_ranges):
        ranges_ind = {}
        for dim in region_ranges:
            if dim == 'lons': # Convert the region_ranges if needed
                bounds = ([lon180(bound) for bound in region_ranges[dim]] 
                          if self._grid[dim][0] < 0 else 
                          [lon360(bound) for bound in region_ranges[dim]])
                
            elif region_ranges[dim][0] > region_ranges[dim][1]:
                print("Lower bound should be smaller than upper bound!")
                return 
            
            else:
                bounds = region_ranges[dim]
            
            ranges_ind[dim] = bound_to_index(self._grid[dim],bounds)

        indices = []
        for dim in self._axis_names:            

            if dim in ranges_ind:
                region_ranges = ranges_ind[dim]
                for bounds in region_ranges:            
                    if bounds[0] != bounds[1]:        
                        indices.append([i for i in range(bounds[0],bounds[1])])
                    else:
                        indices.append([bounds[0]])
            else:                    
                indices.append([i for i in range(self._dims[dim])])

        index_arrays = np.ix_(*indices)
        return index_arrays

    def get_values_region(self, region_ranges=None, keys=[],mask=None):
        """
        Return a list of tuples of values at each grid point within the specified region
        
        Variables:
        - region_ranges: Dict which specifies the ranges in each dim
          e.g. {'lons':[0,100], 'lats':[0,60]}

        """
        if not keys: keys = [key for key in self._data if len(self._data[key].shape) == len(self._axis_names)]

        if not region_ranges:
            values = {}
            for key in keys:
                data = np.ma.array(self._data[key],mask=mask)
                values[key] = data[data.mask==False].data
            return pd.DataFrame(values,columns=keys)

        index_arrays = self.get_region_index_array(region_ranges)

        values = {}
        for key in keys:            
            data = np.ma.array(self._data[key],mask=mask)[index_arrays]
            values[key] = data[data.mask==False].data        
        
        return pd.DataFrame(values,columns=keys)

    def get_point_data(self,lat,lon,**kwargs):
        return self.get_values_region({'lats':[lat-0.01,lat+0.01],'lons':[lon-0.01,lon+0.01]},**kwargs)

    def generate_point_data(self,site_info,lat_name='Latitude',lon_name='Longitude',**kwargs):
        point_data = PointData()
        point_data.set_site_info(site_info)
        for site in site_info.index:
            print('Generate data at ', site)
            lat = site_info.loc[site,lat_name]
            lon = site_info.loc[site,lon_name]
            data = self.get_point_data(lat,lon,**kwargs)
            data['Site name'] = site
            point_data._all_data = point_data._all_data.append(data)

        point_data._all_data = point_data._all_data.reset_index().rename(columns={'index':'time_index'})

        return point_data

    def get_fractions(self,groups,region_ranges=None,**kwargs):
        '''
        groups: {'AOD':{'tauca':'Carb','taudu':'Dust','tausu':'Sulf','tausa':'Salt'},
                 'mass':{'cmasst':'OC','cmasstbc':'BC','dmasst':'Dust','smasst':'Sulf','samasst':'Salt'}}
        '''
        
        data = self.get_values_region(region_ranges=region_ranges,**kwargs)
        total = data.sum()

        fractions = {key:total[groups[key].keys()]/total[groups[key].keys()].sum()
                        for key in groups}

        return {key:fractions[key].rename(groups[key]) for key in groups}

    def get_fractions_intervals(self,groups,intervals,axis_name,region_ranges={},**kwargs):
        
        data = collections.defaultdict(list)
        for i in range(len(intervals)-1):

            bounds = intervals[i:i+2]
            fractions = self.get_fractions(groups,{axis_name:bounds,**region_ranges},**kwargs)
            for key in fractions:
                data[key].append(fractions[key])
  
        return {key:pd.DataFrame(data[key]) for key in data}

