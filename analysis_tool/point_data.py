from base_data import Data
from analysis_utils import filter_time

import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import cartopy.crs as ccrs

info_columns = ['Latitude','Longitude','Altitude',
                'Start date','End date','Records']

class PointData(Data):
    def __init__(self):
        Data.__init__(self)
        self._site_info = pd.DataFrame(columns=info_columns)
        self._site_info.index.name = 'Site name'
        self._all_data = pd.DataFrame(columns=['Site name'])
        self._avg_by = 'Site name'

    def get_all_data(self):
        return self._all_data 

    def get_site_info(self):
        return self._site_info

    def set_site_info(self,df,columns=['Latitude', 'Longitude','Altitude']):
        self._site_info = df[columns]
        return

    def site_avg(self,period=None, year=None,site_info_columns=['Latitude', 'Longitude','Altitude']):
        df = (filter_time(self._all_data,'Start date',period=period,year=year)
             .groupby(by=self._avg_by).agg(['mean','count','std']))
        return df if not site_info_columns else df.merge(self._site_info[site_info_columns],left_index=True,right_index=True)

    def annual_avg(self):
        pass

    def plot_data_range(self,varlist,figsize=(8,10)):
        year2mdate = lambda x: mdates.date2num(datetime.datetime(x.year,1,1))
        start_year = year2mdate(self._all_data['Start date'].min())
        end_year = year2mdate(self._all_data['Start date'].max())
        sites = self._all_data['Site name'].unique()
        nsites = len(sites)
        res = []
        for var in varlist:
            fig,ax = plt.subplots(figsize=figsize)
            filtered = self._all_data[self._all_data[var]==self._all_data[var]]
            
            for i,site in enumerate(sites):
                data = filtered[filtered['Site name']==site]['Start date']
                plt.plot(data,[i]*len(data),'k|')

            plt.title(var)
            plt.ylim([-1,nsites])
            plt.xlim([start_year,end_year])
            plt.yticks(list(range(0,nsites)),sites,fontsize=12)
            plt.xticks(fontsize=12)
            plt.tight_layout()
            res.append(fig)

        return res

    def plot_sites(self,avg,val_column,title='',cmap='Reds',text=None):
        fig = plt.figure(figsize=(10,4))
        ax = plt.axes(projection=ccrs.PlateCarree())
        ax.coastlines()

        plt.scatter(avg['Longitude'],avg['Latitude'],
                s=60, edgecolor='k',c=av[val_column], cmap=cmap,
                transform=ccrs.PlateCarree()
                )
        plt.colorbar(extend='both')
        if text: plt.text(text[0],text[1],text[2],rotation=-90)

        plt.title(title)
        plt.tight_layout()

    