from base_data import Data
from grid_info import GridInfo
from analysis_utils import bound_to_index, lon360, lon180, ax_set
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

    def axis_avg(self,axes_names=['time'],selections={}):
        res = {}
        for key in self._data:
            avg = self._data[key].copy()
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

        return res

    def plot_grid(self,data=None,param=None,selections={},ax=None,cbounds=None,cmap='Reds',colorbar=True,mask=None,key2=None,cax=None,**kwargs):

        projection = ccrs.PlateCarree()

        norm = mcolors.BoundaryNorm(cbounds, ncolors=256) if cbounds else None

        if not ax: fig, ax = plt.subplots(figsize=(10,4),subplot_kw={'projection': ccrs.PlateCarree()})
        
        x = self.get_grid('lons')
        y = self.get_grid('lats')
        if not data:        
            data = self.axis_avg(axes_names=[axis 
                                            for axis in self._axis_names 
                                            if axis not in ['lats','lons']],
                                            selections=selections)[param]
        data = np.squeeze(data)
        print(data.shape)

        # if key2:
        #     data = data-self.get_data()[key2][z]

        # if type(mask) == np.ndarray: 
        #     data = np.ma.array(data, mask = mask)
        #     print(data.shape,mask.shape)       

        ax.coastlines()
        ax.set_xticks(np.linspace(-180, 180, 5), crs=projection)
        ax.set_yticks(np.linspace(-90, 90, 5), crs=projection)

        # ax_settings = {
        #     'xlim': [-180,180],
        #     'ylim':[-90,90]
        # }
        # ax_set(ax,**ax_settings,**kwargs)

        pcm=ax.pcolormesh(x,y,data,cmap=cmap,norm=norm)

        if colorbar: 
            cb = plt.colorbar(pcm,ax=ax,extend='max')           

        return ax

    def get_values_region(self,region_ranges=None):
        """
        Return a list of tuples of values at each grid point within the specified region
        
        Variables:
        - region_ranges: Dict which specifies the ranges in each dim
          e.g. {'lons':[0,100], 'lats':[0,60]}

        """
        if not region_ranges:
            values = {key: self._data[key].flatten() for key in self._data}
            return pd.DataFrame(values,columns=self._data.keys())

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

        #     if 'satellite' in self._axis_names:
        #         print(dim,ranges_ind[dim])
        #         print(bounds,self._grid[dim][ranges_ind[dim]])
        # print(ranges_ind)

        values = {}
        for key in self._data:
            indices = []
            for dim in self._axis_names:
                if dim in ranges_ind:
                    region_ranges = ranges_ind[dim]
                    for bounds in region_ranges:                    
                        indices.append([i for i in range(bounds[0],bounds[1])])
                else:                    
                    indices.append([i for i in range(self._dims[dim])])

            index_arrays = np.ix_(*indices)
            values[key] = self._data[key][index_arrays].flatten()
        
        
        return pd.DataFrame(values,columns=self._data.keys())

    def get_fractions(self,groups,region_ranges=None):
        '''
        groups: {'AOD':{'tauca':'Carb','taudu':'Dust','tausu':'Sulf','tausa':'Salt'},
                 'mass':{'cmasst':'OC','cmasstbc':'BC','dmasst':'Dust','smasst':'Sulf','samasst':'Salt'}}
        '''
        
        data = self.get_values_region(region_ranges=region_ranges)
        total = data.sum()
        fractions = {key:total[groups[key].keys()]/total[groups[key].keys()].sum()
                        for key in groups}

        return {key:fractions[key].rename(groups[key]) for key in groups}

    def get_fractions_intervals(self,groups,intervals,axis_name,region_ranges={}):
        
        data = collections.defaultdict(list)
        for i in range(len(intervals)-1):
            bounds = intervals[i:i+2]
            fractions = self.get_fractions(groups,{axis_name:bounds,**region_ranges})
            for key in fractions:
                data[key].append(fractions[key])
  
        return {key:pd.DataFrame(data[key]) for key in data}
