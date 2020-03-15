"""
This module contains the class `FluxData` for reading mass and flux data from given list of files in three categories:

- Source
- Sink
- Mass

"""
from base_data import Data
from analysis_utils import draw_progress_bar,grid_area, ga_open_file, ax_set
from grads_wrapper import GradsWrapper

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

class Flux():

    def __init__(self,data={}):
        self.data = data

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self,data):
        self._data = data
        self._sum = np.array(list(data.values())).sum(axis=0)
        self._fractions = {key:data[key]/self._sum for key in data}

    @property
    def sum(self):
        return self._sum

    @property
    def fractions(self):
        return self._fractions

class ModelFluxData(Data):
    """class ModelFluxData

    """
    def __init__(self,zrange=[1,1],time_ranges=[[1,1]],prefix='',suffix='',filedir='',**kwargs):
        Data.__init__(self)

        self.filedir = filedir
        self.prefix = prefix
        self.suffix = suffix
        self.zrange = zrange
        self.tranges = time_ranges

        self._sources = Flux()
        self._sinks = Flux()
        self._masses = Flux()
 
    ## Simple getter/setter
    @property
    def filedir(self):
        return self._filedir

    @filedir.setter
    def filedir(self,filedir):
        self._filedir = filedir

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self,prefix):
        self._prefix = prefix

    @property
    def suffix(self):
        return self._suffix

    @suffix.setter
    def suffix(self,suffix):
        self._suffix = suffix

    @property
    def tranges(self):
        return self._tranges

    @tranges.setter
    def tranges(self,time_ranges):
        self._tranges = time_ranges

    @property
    def zrange(self):
        return self._zrange

    @property
    def nz(self):
        return self._nz

    @zrange.setter
    def zrange(self,zrange):
        self._zrange = zrange
        self._nz = zrange[1]-zrange[0]+1

    @property
    def sources(self):
        return self._sources

    @property
    def sinks(self):
        return self._sinks

    @property
    def masses(self):
        return self._masses

    ###############################################

    ## Read data from files
    def read_aave_single(self,filename,time=1,z=1,**kwargs):
        ga = GradsWrapper()
        ga.open(self._filedir,filename)
        ga.zlevel(z)
        ga.time(time)
        data = ga.aave(filename,**kwargs)
        ga.close()
        return data
        
    def read_aave(self,grads_names,
                  lons=[-180,180],lats=[-90,90],
                  time=3600*35*365,check='check',op='',
                  screen_negative=True,**kwargs): 
        
        area = grid_area(lats,lons)
        op = '*{}*{}{}'.format(area,time,op)
        tint = [t[1]-t[0]+1 for t in self._tranges]
        ttotal = sum(tint)

        processed = 0
        data_num = len(grads_names)*len([t for t in self._tranges if 0 not in t])*self._nz

        ga = GradsWrapper(print=False)
        data = {}
        for grads_name in grads_names:
            data[grads_name] = np.zeros((self._nz,))
            for i,trange in enumerate(self._tranges):
                if 0 in trange: continue
                filename = self.prefix + grads_name + self.suffix
                ga_open_file(ga,self.filedir,filename,check,i,None,self._tranges)
                for j,z in enumerate(range(self._zrange[0],self._zrange[1]+1)):
                    ga.zlevel(z)        
                    data[grads_name][j] +=  ga.aave(filename,trange=trange,op=op,**kwargs) *tint[i]/ttotal
                    
                    processed += 1
                    draw_progress_bar(processed/data_num)

                ga.close()

            
            for j in range(self.nz):
                if 'mass' in grads_name:
                    print('mass', grads_name, data[grads_name][j])
                data[grads_name][j] = max(data[grads_name][j],0) if screen_negative else abs(data[grads_name][j])
        return data

    def read_sources(self,sources,**kwargs):
        self._sources.data = self.read_aave(sources,**kwargs)

    def read_sinks(self,sinks,op='',**kwargs):
        self._sinks.data = self.read_aave(sinks,op=op+'*(-1)',**kwargs)

    def read_masses(self,masses,**kwargs):
        self._masses.data = self.read_aave(masses,time=1,**kwargs)

    def read_all(self,var_dict,**kwargs):
        for key in ['sources','sinks','masses']:
            if key in var_dict:
                print(f'\nReading {key}')
                getattr(self,f'read_{key}')(var_dict[key],**kwargs)

    def make_df(self):

        # All data
        df = pd.DataFrame()
        for key in ['sources','sinks','masses']:
            data = getattr(self,key).data
            for key2 in data:
                df[f'{key}:{key2}'] = data[key2]

        # Sum
        for key in ['sources','sinks','masses']:
            df[f'SUM({key})'] = getattr(self,key).sum
        
        # Fraction
        for key in ['sources','sinks','masses']:
            fractions = getattr(self,key).fractions
            for key2 in fractions:
                df[f'{key}: {key2}(%)'] = fractions[key2]*100

        return df

    def plot_barh(self,item='sinks',scale=1,**kwargs):
        """ Plot the fractions """
        
        left = 0
        x = list(range(self.nz))

        fig,ax = plt.subplots()
        fractions = getattr(self,item).fractions
        for key in fractions:
            ax.barh(x,fractions[key]*scale,left=left,label=key)
            left += fractions[key]*scale

        ax_set(ax,**kwargs)
        ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.1),
          fancybox=True, shadow=True, ncol=5)

        
    
    





