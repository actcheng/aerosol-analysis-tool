"""    
This module contains the class `NasData` which  read and analyze the data presented in NASA-Ames format. 

Example:
    >> nas_data = NasData()
    >> nas_data.read_nas(filename)
or 
    >> nas_data.read_nas_all(filelist,path='X/')

Attributes:
    NasData():

Utils
"""
from point_data import PointData
from analysis_utils import day_to_date, draw_progress_bar, remove_outlier
import pandas as pd
import numpy as np
from scipy import stats
import datetime

fields_required = {'Station name':      lambda x: x, 
                   'Station latitude':  lambda x: float(x),
                   'Station longitude': lambda x: float(x),
                   'Station altitude':  lambda x: float(x[:-1]),
                   'File name':         lambda x:x }

header_to_site = {'Station latitude': 'Latitude',
                  'Station longitude': 'Longitude',
                  'Station altitude': 'Altitude',
                  'Start date':'Start date',
                  'End date':'End date'}

class NasData(PointData):
    """class NasData

    Attributes:

    Methods:
        read_nas_all(filelist)
        read_nas
        read_header
        read_values

    """
    
    def __init__(self):
        PointData.__init__(self)
        self._header_info = pd.DataFrame()

    def read_nas_all(self,filelist,path='',fields='all',read_values=True):

        for i,file in enumerate(filelist):
            self.read_nas(path+file,fields=fields,read_values=read_values)
            draw_progress_bar((i+1)/len(filelist))

        print(f'\nFinished reading {len(filelist)} files in directory {path}')
        return 

    def read_nas(self,filename,fields='all',read_values=True):
        ## Read headers

        headers, n_header, n_records = self.read_header(filename,fields=fields)
        if not headers: return

        # append to _header_info
        self._header_info = self._header_info.append(headers,ignore_index=True)

        # Add site to self._site_info
        site_name = headers['Station name']  
        start_date = headers['Start date']

        if site_name not in self._site_info.index:
            this_site_info = {header_to_site[field]: headers[field] for field in header_to_site}
            this_site_info['Records'] = n_records
            self._site_info.loc[site_name] = pd.Series(this_site_info)
        else:
            # Update dates and record number
            self._site_info.at[site_name,'Start date'] = min(self._site_info.at[site_name,'Start date'], headers['Start date'])
            self._site_info.at[site_name,'End date'] = max(self._site_info.at[site_name,'End date'], headers['End date'])
            self._site_info.at[site_name,'Records'] += n_records

        
        if read_values:
            # Read values
            values = self.read_values(filename,n_header)
            values['Site name'] = site_name
            # Replace undef to np.nan
            for col in values.columns:
                if col in headers['Undef']:
                    if values[col].dtypes != type(headers['Undef'][col]):
                        values[col] = values[col].astype(type(headers['Undef'][col]))
                    values[col] = values[col].mask(np.isclose(values[col], headers['Undef'][col]))
                    # Remove outliers
                if values[col].dtypes == float and 'time' not in col:
                    # values[col] = values[col].mask(np.abs(stats.zscore(values[col])) > 3)
                    values[col] = remove_outlier(values[col])

            # Change starttime, endtime types
            for time,date in [('starttime','Start date'),('endtime','End date')]:
                values[date] = values.apply(lambda x: day_to_date(start_date,x[time]),axis=1)
                values = values.drop(columns=[time])
            cols = list(values.columns)

            values = values[cols[-3:]+cols[:-3]]
            
            # Concat to _all_data
            self._all_data = pd.concat([self._all_data,values],ignore_index=True,sort=True)

        return 

    def read_header(self,filename,fields='all'):
        
        try: 
            infile = open(filename)
            data = infile.readlines()        
            infile.close()
        except:
            print('\nError in reading ', filename)
            return None, None, None

        n_header = int(data[0].split()[0])
        n_records = len(data)-n_header

        campaign = data[4].split()
        start_date = datetime.datetime.strptime(data[6][:10], '%Y %M %d')
        end_date = start_date + datetime.timedelta(float(data[-1].split()[1]))
        undef = {}
        for key,value in zip(data[n_header-1].split()[1:],data[11].split()):
            if key in undef:
                i = 1
                while f'{key}.{i}' in undef:
                    i+=1 
                undef[f'{key}.{i}'] = float(value)
            else:
                undef[key]=float(value)
        # undef = {key:float(value) for key,value in zip(data[n_header-1].split()[1:],data[11].split())}

        headers = {'n_header': n_header,
                    'Campaign': campaign,
                    'Start date': start_date,
                    'End date': end_date,
                    'Undef': undef}

        for row in data[:n_header]:
            if ':' in row and len(row.split(':'))==2:
                [field, info] = row.split(':')
                if field in fields_required: 
                    headers[field.strip()] = fields_required[field](info.strip()) 
                elif fields == 'all' or field in fields:
                    headers[field.strip()] = info.strip()
        return headers, n_header, n_records

    def read_values(self,filename,n_header):
        data = pd.read_csv(filename,header=n_header-1,sep="\s+|;|:")
        return data 

    def tidy_data(self):
        cols = ['Site name','Start date','End date']
        cols += [col for col in self._all_data.columns if col not in cols]
        to_drop = [col for col in self._all_data.columns if 'flag' in col]

        self._all_data = self._all_data[cols].drop(columns=to_drop)