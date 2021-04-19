from point_data import PointData
from grads_wrapper import GradsWrapper
from analysis_utils import draw_progress_bar, ga_open_file
import pandas as pd
import numpy as np
import datetime 
import os
import sys

class ModelPointData(PointData):
    def __init__(self):
        PointData.__init__(self)
        self._sites = set()
        self._avg_data = pd.DataFrame()

    def get_avg_data(self):
        return self._avg_data

    def read_grads_all(self,grads_dir,grads_names,start_dates,               
                       time_ranges=[1,1],file_suffixes=None,
                       zrange=None,check='check',
                       show_progress=True, save=True,
                       deltaseconds=60*60*24,**kwargs):
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
            
        data_num = len(grads_names)*len(self._site_info.index)*len(time_ranges)
        processed = 0

        ga = GradsWrapper()
        all_data = pd.DataFrame()     
        for grads_name in grads_names:
            df = pd.DataFrame()
            for i in range(len(time_ranges)):

                time_range,date_list = time_ranges[i],date_lists[i]
                
                ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges)     

                for site in self._site_info.index[:]:
                    lat,lon = self._site_info.loc[site,'Latitude'],self._site_info.loc[site,'Longitude']
                    ga.locate(lat,lon)
                    try:    
                        if zrange:
                            df_site = pd.DataFrame([[site]*len(date_list),date_list],
                                        index=['Site name','Start date']).T
                            names = [f'{grads_name}.{z}' for z in range(zrange[0],zrange[1]+1)]
                            for i in range(len(names)):
                                z = zrange[0]+i
                                name = f'{grads_name}.{z}'
                                ga.zlevel(z)
                                out = ga.tloop(grads_name,time_range,**kwargs)
                                df_site[name] = out
                        else:
                            names = [grads_name]
                            out = ga.tloop(grads_name,time_range,**kwargs)
                            df_site = pd.DataFrame([[site]*date_len,date_list,out],
                                            index=['Site name','Start date',grads_name]).T
                            
                        df = pd.concat([df,df_site],ignore_index=True,sort=False)

                    except:
                        print(f'Error in getting data at {site} (lat: {lat}, lon:{lon})')
                    
                    processed+=1
                    if show_progress: 
                        draw_progress_bar(processed/data_num)
                    else:
                        print(f'Finished reading {processed}/{data_num}')
                        sys.stdout.flush()
                ga.close()

            df[names] = df[names].astype(float)
            
            if len(all_data):
                    all_data = all_data.merge(df,on=['Site name','Start date'],how='outer')
            else:
                all_data = df

        if save:
            self._all_data = all_data
        else:
            return all_data

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
                ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges)
                  
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
                    if show_progress: 
                        draw_progress_bar(processed/data_num)
                    # else:
                    #     print(f'Finished reading {processed}/{data_num}')
                    #     sys.stdout.flush()
                ga.close()

        self._avg_data = df_avg 
        return df_avg

    def get_grads_median(self,*args,**kwargs):

        all_data = (self.read_grads_all(*args,**kwargs,save=False)
                        .drop(['Start date'],axis=1)
                        .groupby('Site name')
                        .median())
      
        return all_data

    
