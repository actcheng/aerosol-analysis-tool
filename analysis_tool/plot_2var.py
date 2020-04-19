import pandas as pd
import matplotlib.pyplot as plt

class Plot2Var():

    def __init__(self,data,xname,yname):
        self.data = data
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
    def plot_mean(self,intervals,plot_std=True,color='k',marker='o'):
        groupby = self.data.groupby(pd.cut(self.data[self.xname],intervals))
        mean = groupby.mean()
        x = pd.IntervalIndex(mean.index).mid
        y = mean[self.yname]
        
        plt.scatter(x,y,color=color,marker=marker)
        if plot_std:
            yerr = groupby.std()[self.yname]
            plt.errorbar(x,y,yerr=yerr,ls='none',color=color)
        
        return 

    def plot_hist(self,interval_dict):
        pass

