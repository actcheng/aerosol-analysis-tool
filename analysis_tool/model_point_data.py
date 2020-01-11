from point_data import PointData
from grads_wrapper import GradsWrapper
from analysis_utils import draw_progress_bar
import pandas as pd
import numpy as np
import datetime 
import os


class ModelPointData(PointData):
    def __init__(self):
        PointData.__init__(self)
        self._sites = set()
        self._avg_data = pd.DataFrame()

    def get_avg_data(self):
        return self._avg_data

    def read_grads_all(self,grads_dir,grads_names,start_dates,
                       time_ranges=[1,1],file_suffixes=None,
                       check='check',deltaseconds=60*60*24,**kwargs):
        if type(grads_names) != list: grads_names = [grads_names]
        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        if type(start_dates) != list: start_dates = [start_dates] 

        # Create date lists
        this_date = start_dates[0]
        date_lists = []
        for i, time_range in enumerate(time_ranges):
            date_len = time_range[1]-time_range[0] +1
            date_list = [0]*date_len
            date_list[0] = this_date
            for j in range(1,date_len):
                date_list[j] = date_list[j-1] + datetime.timedelta(seconds=deltaseconds)
            date_lists.append(date_list)
            if len(start_dates) > i+1:                
                this_date = start_dates[i+1]
            else:
                this_date = date_list[-1] + datetime.timedelta(seconds=deltaseconds) 
            
        ga = GradsWrapper()
        all_data = pd.DataFrame()        
        for grads_name in grads_names:
            df = pd.DataFrame()
            for i in range(len(time_ranges)):
                time_range,date_list = time_ranges[i],date_lists[i]
                if len(time_ranges) > 1:
                    if file_suffixes:
                        ga.open(f'{grads_dir}_{file_suffixes[i]}/{check}',grads_name)
                    else:
                        ga.open(f'{grads_dir}_{i+1}/{check}',grads_name)
                else:
                    ga.open(f'{grads_dir}/{check}',grads_name)          
                for site in self._site_info.index[:]:
                    lat,lon = self._site_info.loc[site,'Latitude'],self._site_info.loc[site,'Longitude']
                    try:
                        ga.locate(lat,lon)
                        out = ga.tloop(grads_name,time_range,**kwargs)
                        df_site = pd.DataFrame([[site]*date_len,date_list,out],
                                        index=['Site name','Start date',grads_name]).T
                        
                        df = pd.concat([df,df_site],ignore_index=True,sort=False)
                    except:
                        print(f'Error in getting data at {site} (lat: {lat}, lon:{lon})')
                ga.close()
            df[grads_name] = df[grads_name].astype(float)
            if len(all_data):
                    all_data = all_data.merge(df,on=['Site name','Start date'],how='outer')
            else:
                all_data = df
        self._all_data = all_data
        return 

    def get_grads_avg(self,grads_dir,grads_names,
                      time_ranges=[1,1],file_suffixes=None,
                      zrange=None,check='check',show_progress=True,**kwargs):

        if type(time_ranges[0]) != list: time_ranges = [time_ranges]
        ttotal = sum(t[1]-t[0]+1 for t in time_ranges)
        df_avg = self._site_info.copy()
        ga = GradsWrapper()

        data_num = len(grads_names)*len(self._site_info.index)*len(time_ranges)
        processed = 0

        for grads_name in grads_names:
            for i in range(len(time_ranges)):
                trange = time_ranges[i]
                if len(time_ranges) > 1:
                    if file_suffixes:
                        ga.open(f'{grads_dir}_{file_suffixes[i]}/{check}',grads_name)
                    else:
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
                    processed+=1
                    if show_progress: draw_progress_bar(processed/data_num)

                ga.close()

        self._avg_data = df_avg 
        return df_avg


    