from type_size_info import TypeSizeInfo
from point_data import PointData

# from analysis_utils import day_to_date, get_filelist

import pandas as pd
import numpy as np
import datetime

class AeronetData(PointData,TypeSizeInfo):
    def __init__(self):
        PointData.__init__(self)
        TypeSizeInfo.__init__(self,'AERONET','aero','bin',bin_num=22)

        self.set_bin_centers([x*2 for x in [0.05,0.065604, 0.086077, 0.112939, 0.148184,
             0.194429, 0.255105, 0.334716, 0.439173, 0.576227,
             0.756052, 0.991996, 1.301571, 1.707757, 2.240702,
             2.939966, 3.857452, 5.06126, 6.640745, 8.713145,
             11.432287, 15.0]])

    def read_old_pickle(self,pickle_name):

        new_colnames = {
            'AERONET_Site_Name': 'Site name',
            'Date(dd:mm:yyyy)' : 'Start date',
            'Site_Latitude(Degrees)': 'Latitude',
            'Site_Longitude(Degrees)': 'Longitude',
            'AOD_500nm': 'AOD',
            '440-870_Angstrom_Exponent': 'Angstrom Exponent'
        }

        site_col = ['Latitude','Longitude'] 
        for i in range(1,23):
            new_colnames[f'Bin {i}'] = f'dvdlnr.{i}'
        df = pd.read_pickle(pickle_name)[new_colnames.keys()].rename(columns=new_colnames)


        self._site_info = df.groupby('Site name').mean()[site_col]
        self._all_data = df.drop(columns=site_col)

        self._site_info['Records'] = self.site_avg(agg=['count'],site_info_columns=site_col)[('Start date', 'count')]