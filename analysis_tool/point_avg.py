from analysis_utils import ax_selector
from base_data import Data

import pandas as pd
import matplotlib.pyplot as plt

'''''
Example input:

avg_info = {'Orig':model_avg['scont_sfc'],
          'Bin':model_avg_bin['scont_sfc'],
          'Ebas2006: SO4':ebas_avg_2006[('SO4--', 'mean')],
          'EbasAll: SO4':ebas_avg[('SO4--', 'mean')],
          'Ebas2006: XSO4':ebas_avg_2006[('XSO4--', 'mean')],
          'EbasAll: XSO4':ebas_avg[('XSO4--', 'mean')]}

'''''

class PointAvg(Data):
    def __init__(self,avg_info=None,site_info=None):
        Data.__init__(self)
        if avg_info and site_info:
            self._avg_info = avg_info 
            self._avg_data = site_info.join(pd.DataFrame([avg_info[key].rename(key) for key in avg_info]).T) 

    def get_avg_data(self):
        return self._avg_data

    def get_avg_info(self):
        return self._avg_info

    def get_sites(self):
        return list(self._avg_data.index.get_level_values('Site name').unique())

    def plot_scatter(self,model_labels,obs_labels,xlim=[0,1.2],ylim=[0,0.2],model_err=None,obs_err=None,savename=None):
        corr = self._avg_data [model_labels+obs_labels].corr()
        ncols=len(model_labels)
        nrows=len(obs_labels)
        fig, axes = plt.subplots(ncols=ncols,nrows=nrows,figsize=(ncols*4.5,nrows*4))
        for i in range(nrows):
            for j in range(ncols):
                ax = ax_selector(axes,i,j,nrows,ncols)
                self._avg_data.plot.scatter(obs_labels[i],model_labels[j],ax=ax)
                if model_err or obs_err:
                    plt.errorbar(obs_labels[i],model_labels[j],xerr=obs_err[j],data=self._avg_data,fmt="none")
                ax.set_xlim(xlim)
                ax.set_ylim(ylim)
                rtop = max(xlim[1],ylim[1])
                ax.plot([0,rtop],[0,rtop],'k')
                ax.set_title('Corr={0:.2f}'.format(corr.at[obs_labels[i],model_labels[j]]))
                plt.tight_layout()

        if savename: plt.savefig(savename)

    def plot_site_months(self,site,cases,ax=None,ylim=[10,10000],errs=None,figsize=(5,5)):
        """ 
        Plot monthly values at specified site for different cases (obs, model)
          - site: site name
          - cases: dict with key=column name, value=plot style
          - errs: dict with key=data column, value=std column
        """
        site_df = self.filter_site(site)
        time = site_df['Start date']
        if not ax:
            fig,ax = plt.subplots(figsize=figsize)
        for key in cases:
            ax.semilogy('Start date',key,cases[key],data=site_df,markersize=10,label=key)
        if errs:
            for key in errs:
                plt.errorbar('Start date',key,yerr=errs[key],data=site_df,fmt="none",label=None)    
        ax.set_ylim(ylim)
        ax.set_xlabel('Months')
        plt.legend()
        plt.title(site,fontsize=14)
        
        return 

    def plot_all_sites(self,*args,**kwargs):
        for site in self.get_sites():
           self.plot_site_months(site,*args,**kwargs) 

    def filter_site(self,site):
        return self._avg_data[self._avg_data.index.get_level_values('Site name')==site][list(self._avg_info.keys())].reset_index().drop(columns=['Site name'])


    


        