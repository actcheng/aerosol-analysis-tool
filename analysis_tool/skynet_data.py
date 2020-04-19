from point_data import PointData
from analysis_utils import get_filelist_from_dir, columns_first, draw_progress_bar

import pandas as pd
import numpy as np
import os
import datetime

class SkynetData(PointData):
    def __init__(self):
        PointData.__init__(self)

    def data_to_daily(self):
        self._all_data = self._all_data.groupby(['Site name',pd.Grouper(key='Start date', freq='1D')]).mean().reset_index()

    def read_skynet_all(self,filedir,options=['2006']):
        filelist = filter_version(get_filelist_from_dir(filedir,optional=options))
        for i, filename in enumerate(filelist):
            self.read_skynet_file(os.path.join(filedir,filename))
            draw_progress_bar((i+1)/len(filelist))

        print(f'\nFinished reading {len(filelist)} files in directory {filedir}')
        self._all_data = columns_first(self._all_data,['Site name','Start date'])
        return

    def read_skynet_file(self,filename):

        try: 
            infile = open(filename)
            data = infile.readlines()        
            infile.close()
        except:
            print('\nError in reading ', filename)
            return None, None

        n_header = int(data[0])

        site_name = data[4].split()[0]
        if site_name not in self._site_info.index:
            loc_text = data[4].split('(')[-1].split(',')
            this_site = {}
            this_site['Latitude'] = float(loc_text[0][1:-1]) if loc_text[0][-1] == 'N' else -float(loc_text[0][1:-1])
            this_site['Longitude'] = float(loc_text[1][:-1]) if loc_text[1][-1] == 'E' else -float(loc_text[1][1:-1])
            this_site['Altitude']= float(loc_text[2].split('m')[0])
            self._site_info.loc[site_name] = pd.Series(this_site)

        # Read values
        values = pd.read_csv(filename,header=n_header-2,sep="\s+|;|:")
        
        # Start date
        values['Site name'] = site_name
        values['Start date'] = values.apply(lambda x: 
                                datetime.datetime(int(x['Year']),
                                                  int(x['Month']),
                                                  int(x['Day'])) + 
                                datetime.timedelta(x['Hour(LT)']),axis=1)

        # Filter cloud flag
        values = values[values['CloudFlag']==1]
        
        # Drop columns
        to_drop = ['Year','Month','Day','Hour(LT)','DN(LT)','CloudFlag'] 
        values = values.drop(columns=to_drop)        

        # Concat to _all_data
        self._all_data = pd.concat([self._all_data,values],ignore_index=True)



## Utils
def filter_version(filelist):
    # Pick s01 if avaiable
    site_files = {filename.split('_')[1]:[] for filename in filelist}
    filelist_filtered = []
    for filename in filelist:
        site_files[filename.split('_')[1]].append(filename)

    s_levels = {site : max([int(filename.split('_')[2][1:3])  
                            for filename in site_files[site]])
                 for site in site_files}

    filelist_filtered = [filename 
                         for site in site_files 
                         for filename in site_files[site] 
                         if int(filename.split('_')[2][1:3]) == s_levels[site]]

    return filelist_filtered


        