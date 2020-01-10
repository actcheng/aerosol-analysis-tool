from point_data import PointData
from analysis_utils import *

import pandas as pd
import numpy as np
import os
import datetime

class EusaarData(PointData):
    def __init__(self):
        PointData.__init__(self)
        self._code_dict = {}

    def read_site_info(self,filename):
        """ Required columns: ['Site name','Site code','Latitude','Longitude']"""
        self._site_info = pd.read_csv(filename)
        self._code_dict = (self._site_info[['Site code','Site name']]
                               .set_index(['Site code'])
                               .to_dict()['Site name'])
        self._site_info = self._site_info.set_index('Site name')
    
    def get_code_dict(self):
        return self._code_dict

    def read_time_series(self,filedir,
                        options=['N30','N50','N100','N250','gd'],
                        start_date=datetime.datetime(2008,1,1),length=17545):

        """ Read time series data ([N30], [N50], [N100] and [N250])"""

        filelist = get_filelist_from_dir(filedir,optional=options)
        site_codes = list(get_sites_from_filenames(filelist))
        all_data = pd.DataFrame()

        timevector = hours_to_datelist(start_date,length)
        print('Number of sites: ', len(site_codes))
        for i,site in enumerate(site_codes):

            site_name = self._code_dict[site] if site in self._code_dict else site
            
            site_filelist =  get_filelist(filelist,required=[site])
            site_df = pd.DataFrame(timevector,columns=['Start date'])
            site_df['Site name'] = site_name
            site_df = site_df[['Site name','Start date']]

            for filename in site_filelist:
                infile = open(os.path.join(filedir,filename))
                data = infile.read().split()
                infile.close()
                if 'gd' in filename:
                    data = np.array([int(float(d)) for d in data]).reshape((len(data)//2,2))
                    df = pd.DataFrame(data,columns=['Gooddata','Night'])
                    df['Gooddata'] = df['Gooddata'].replace(0,np.nan)                    
                else:
                    data = np.array([float(d) for d in data])
                    df = pd.DataFrame(data,columns=[get_keyword(filename,options)])
                
                site_df = pd.concat([site_df,df],axis=1)
            print(f'Finished reading {i+1}/{len(site_codes)}: {site_name} ({site})')
            site_df = site_df.dropna().drop(columns=['Gooddata'])
            all_data = pd.concat([all_data,site_df])
            
        self._all_data = all_data
        return         

    def read_size_dist(self,file_list,size_filename):
        """Read size distributions at different sites"""
        # Read diameters
        # Read sizes and label with percentiles (5,15,50,83 and 95)

        pass

    def get_percentile_data(self,percentile=50):
        """ Return data with the specified percentile """
        pass