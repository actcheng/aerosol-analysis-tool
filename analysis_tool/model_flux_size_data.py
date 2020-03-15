import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from analysis_utils import ax_set
from type_size_info import TypeSizeInfo
from model_flux_data import ModelFluxData


class ModelFluxSizeData(ModelFluxData,TypeSizeInfo):

    def __init__(self,aerosol_name,prefix,**kwargs):
        ModelFluxData.__init__(self,**kwargs)
        TypeSizeInfo.__init__(self,aerosol_name,prefix,'bin',**kwargs)

    def plot_size_flux(self,item=('sinks','data'),ax=None,labels=None,legend=True,colors=None,xscale='log',xlabel='Diameter (${\mu}$m)',**kwargs):
        
        if not ax: fig, ax = plt.subplots()
        x = self.bin_centers
        data = getattr(getattr(self,item[0]),item[1])
        y = data.values()
        labels = labels or data.keys()
        ax.stackplot(x,y,labels=labels,colors=colors)        

        ax_settings = {'xscale': xscale, 'xlabel':xlabel,'legend':False}
        ax_set(ax,**ax_settings,**kwargs)
        if legend:
            ax.legend(loc='upper center', bbox_to_anchor=(0.45, -0.2),fancybox=True, shadow=True, ncol=5)

        