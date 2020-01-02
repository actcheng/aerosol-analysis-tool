from point_data import PointData
from grads_wrapper import GradsWrapper
import pandas as pd
import numpy as np
import datetime 
import os


class ModelPointData(PointData):
    def __init__(self):
        PointData.__init__(self)
        self._sites = set()

    def read_grads_all(self,grads_dir,grads_names,start_date,time_range=[1,1],deltaseconds=60*60*24,**kwargs):
        if type(grads_names) != list: grads_names = [grads_names]
        date_len = time_range[1]-time_range[0]+1
        date_list = [0]*date_len

        date_list[0] = start_date
        for i in range(1,date_len):
            date_list[i] = date_list[i-1] + datetime.timedelta(seconds=deltaseconds)
        
        ga = GradsWrapper()
        all_data = pd.DataFrame()
        for grads_name in grads_names:
            ga.open(grads_dir,grads_name)
            df = pd.DataFrame()
            for site in self._site_info.index[:8]:
                lat,lon = self._site_info.loc[site,'Latitude'],self._site_info.loc[site,'Longitude']
                try:
                    ga.locate(lat,lon)
                    out = ga.tloop(grads_name,time_range,**kwargs)
                    df_site = pd.DataFrame([[site]*date_len,date_list,out],
                                    index=['Site name','Start date',grads_name]).T
                    
                    df = pd.concat([df,df_site],ignore_index=True,sort=False)
                except:
                    print(f'Error in getting data at {site} (lat: {lat}, lon:{lon})')
            if len(all_data):
                all_data = all_data.merge(df,on=['Site name','Start date'],how='outer')
            else:
                all_data = df
            ga.close()
        self._all_data = all_data
        return 

    def get_grads_avg(self,grads_dir,grads_names,time_ranges=[1,1],zrange=None,check='check',**kwargs):

        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        ttotal = sum(t[1]-t[0]+1 for t in time_ranges)
        df_avg = self._site_info.copy()
        ga = GradsWrapper()

        for grads_name in grads_names:
            for i in range(len(time_ranges)):
                trange = time_ranges[i]
                if len(time_ranges) > 1:
                    ga.open(f'{grads_dir}_{i+1}/{check}',grads_name)
                else:
                    ga.open(f'{grads_dir}/{check}',grads_name)
                for site in self._site_info.index[:]:
                    lat,lon = self._site_info.loc[site,'Latitude'],self._site_info.loc[site,'Longitude']
                    value = ga.get_single_point(grads_name,lat,lon,trange=trange,zrange=zrange,**kwargs) *(trange[1]-trange[0]+1)/ttotal
                    if type(value) == float:
                        df_avg.at[site,grads_name] = value + (df_avg.at[site,grads_name] if i>0 else 0)
                    else:
                        for j in range(len(value)):
                            name = f'{grads_name}.{j+1}'
                            df_avg.at[site,name] = value[j] + (df_avg.at[site,name] if i>0 else 0)

                ga.close()

        return df_avg


    