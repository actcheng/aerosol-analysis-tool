import pandas as pd
import matplotlib.pyplot as plt
from analysis_utils import ax_set
import numpy as np
import matplotlib.colors as mcolors

class Plot2Var():

    def __init__(self,data,xname,yname):
        self.data = data[[xname,yname]].dropna()
        self._xname = xname
        self._yname = yname

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self,data):
        self._data = data

    @property
    def xname(self):
        return self._xname

    @property
    def yname(self):
        return self._yname

    ### Plot means & sd of data, grouped by x intervals
    def plot_mean(self,intervals,plot_std=True,color='k',marker='o',ax=None,label=None,**kwargs):
        groupby = self.data.groupby(pd.cut(self.data[self.xname],intervals))
        mean = groupby.mean()
        x = pd.IntervalIndex(mean.index).mid
        y = mean[self.yname]
        
        if not ax: fig, ax = plt.subplots()

        ax.scatter(x,y,color=color,marker=marker,label=label)
        if plot_std is True:
            yerr = groupby.std()[self.yname]
            ax.errorbar(x,y,yerr=yerr,ls='none',color=color)
        
        ax_set(ax,**kwargs)
        return 

    def plot_hist(self,xedges,yedges,ax=None,bounds=None,density=True,cmap='Reds',colorbar=True,**kwargs):

        if not ax: fig, ax = plt.subplots()
        norm = mcolors.BoundaryNorm(bounds, ncolors=256) if bounds else None

        n = len(self.data[self.xname])
        print('n', n)
        if n <= 1: 
            print('No data')
            return

        weights = np.ones(n)/n if density else np.ones(n)
        try: 
            pcm = ax.hist2d(self.data[self.xname],self.data[self.yname],bins=[xedges,yedges],weights=weights,cmap=cmap,norm=norm)
        except:
            print(self.data.dtypes)
            print(self.data[self.xname])
            print(self.data[self.yname])
            pcm = ax.hist2d(self.data[self.xname],self.data[self.yname],bins=[xedges,yedges],weights=weights,cmap=cmap,norm=norm)
        if colorbar: plt.colorbar(pcm[3],ax=ax,extend='both')

        ax_set(ax,legend=False,**kwargs)
        return pcm

    def plot_counts(self,intervals,plot_std=True,color='k',marker='o',ax=None,label=None,**kwargs):
        groupby = self.data.groupby(pd.cut(self.data[self.xname],intervals))
        counts = groupby.count()
        x = pd.IntervalIndex(counts.index).mid
        y = counts[self.yname]
        
        if not ax: fig, ax = plt.subplots()

        ax.plot(x,y,color=color,label=label)

        ax_set(ax,**kwargs)
        return 

