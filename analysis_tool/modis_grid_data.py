from grid_data import GridData
from analysis_utils import dt64_to_dt, ax_set

import os
import pandas as pd
import numpy as np
from pyhdf.SD import SD, SDC
import datetime
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

month_accum    = [1,32,60,91,121,152,182,213,244,274,305,335]
# month_accum    = [1,32,60,91,122,153,183,214,245,275,306,336]

field_name = {'aod':                "Aerosol_Optical_Depth_Land_Ocean_Mean_Mean",
              'aod_std':            "Aerosol_Optical_Depth_Land_Ocean_Mean_Std",
              'aod_std_mean':       "Aerosol_Optical_Depth_Land_Ocean_Std_Deviation_Mean",
              'aod_hist_counts':    "Aerosol_Optical_Depth_Land_Ocean_Histogram_Counts",
              'aod_db':             "AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Mean",
              'aod_db_std':         "AOD_550_Dark_Target_Deep_Blue_Combined_Mean_Std",
              'aod_db_std_mean':    "AOD_550_Dark_Target_Deep_Blue_Combined_Std_Deviation_Mean",
              'aod_db_hist_counts': "AOD_550_Dark_Target_Deep_Blue_Combined_Histogram_Counts",
              'alfa_ocean':         "Aerosol_AE1_Ocean_JHisto_vs_Opt_Depth",
              'alfa_land':          "Deep_Blue_Angstrom_Exponent_Land_Mean_Mean",
              'alfa_land_std':      "Deep_Blue_Angstrom_Exponent_Land_Mean_Std",
              'alfa_land_std_mean': "Deep_Blue_Angstrom_Exponent_Land_Std_Deviation_Mean",
              'alfa_land_hist_counts': "Deep_Blue_Angstrom_Exponent_Land_Histogram_Counts",
              'aod_small':          "Aerosol_OD_Ratio_Small_Ocean_055_JHisto_vs_Opt_Depth"}

AE_bin_bound_name = "Histogram_Bin_Boundaries"
AE_bin_center = None
AE_name = 'AE_weighed'

satellite_codes = {'MOD': 'Terra', 'MYD':'Aqua'}

class ModisGridData(GridData):

    def __init__(self):
        GridData.__init__(self)
        self._axis_names = ['satellite','time','lats','lons']
        self._masks = {} # Possible masks: valid_obs, ocean_only, land_only
        self._hist_axes = {}

    def read_raw_hdf(self,hdf_names,
                     fields,
                     data_path='',
                     hdf_namelist='hdf_names',
                     time_range=None,
                     hist_attr=None,
                     satellites=['Terra','Aqua'],
                     lons=list(range(-180,180)),
                     lats=list(range(90,-90,-1))):
        '''''
            hdf_names: dataframe of hdf_names
            hdf_namelist: name of txt file of hdf_names
        '''''

        # Get hdf_names
        if hdf_namelist: 
            hdf_names = self.read_hdf_names(data_path+hdf_namelist,time_range,satellites)

        self.set_grid('satellite',sorted(hdf_names['satellite'].unique()))
        self.set_grid('lats',lats)
        self.set_grid('lons',lons)
        dates = sorted(np.array([dt64_to_dt(date) for date in hdf_names['date'].unique()]))
        self.set_grid('time',dates)

        def read_hdf_file(row):
            time_ind = np.searchsorted(self._grid['time'],row['date'])
            sate_ind = np.searchsorted(self._grid['satellite'],row['satellite'])

            filename = os.path.join(data_path,row['hdf_name'])
            hdf = SD(filename,SDC.READ)
            print('Opening ',filename)
            for key in fields:
                field = fields[key]
                print('Reading ', field)

                sds_obj = hdf.select(field)
                data = sds_obj.get()
                attrs = sds_obj.attributes(full=1)
                fillvalue=attrs["_FillValue"]
                add_offset=attrs["add_offset"][0]
                scale_factor=attrs["scale_factor"][0]

                data = (data - add_offset) * scale_factor
                fv = (fillvalue[0]-add_offset)*scale_factor
                data[data == fv] = np.nan                

                if key not in self._data:
                    grid_dims = [self._dims[axis] for axis in self._axis_names]
                    if key in hist_attr:                     
                        # Read bounds and initialize data                        
                        self._hist_axes[key] = {}
                        attrs = sds_obj.attributes(full=1)
                        for i, key2 in enumerate(hist_attr[key]): # hist_attr needed to be in order!
                            bounds = attrs[hist_attr[key][key2]][0]
                            centers = [(bounds[i]+bounds[i+1])/2 for i in range(len(bounds)-1)]
                            self._hist_axes[key][key2] = {'ind': i, 
                                                          'bounds':bounds,
                                                          'centers':centers}
                            grid_dims.append(len(centers))

                    self._data[key] = np.zeros(grid_dims)
                
                if key in hist_attr:
                    self._data[key][sate_ind,time_ind,:,:,:,:] = np.moveaxis(data,[0,1],[2,3])
                else:
                    self._data[key][sate_ind,time_ind,:,:] = data
            hdf.end()

        hdf_names[:].apply(read_hdf_file,axis=1)

    def read_hdf_names(self,hdf_namelist,time_range,satellites):
        print('Reading hdf names from', hdf_namelist)
        infile = open(hdf_namelist)
        data = infile.read().split()
        hdf_names = [x for x in data if 'hdf' in x]
        infile.close()

        data = []
        for hdf_name in hdf_names:
            date, satellite = self.info_from_hdf_name(hdf_name,start_date=time_range[0])
            if (not time_range or time_range[0] <= date <= time_range[1]) and  satellite in satellites:
                data.append({'satellite':satellite,
                                     'date':date,
                                     'hdf_name':hdf_name})
        return pd.DataFrame(data)
    
    def info_from_hdf_name(self,hdf_name,start_date=None):
        data = hdf_name.split('.')
        satellite = satellite_codes[data[0][:3]]
        year, days = int(data[1][1:5]), int(data[1][-3:])

        # try: 
        #     month = month_accum.index(days) + 1 
        #     return datetime.datetime(year,month,15), satellite   
        # except:
        # print('Month not find! days = ', days)
        date = start_date + datetime.timedelta(days=days - 1) 
        return date, satellite   
             
        
        
    def combine_satellites(self):
        self._data = self.axis_avg(['satellite'])
        self.set_grid('satellite',['average'])

    def combine_data(self,data_names,new_data_name):
        '''''
            Fill the nan in data_names[0] with the values in data_names[1]
            e.g. ['alfa_ocean','alfa_land'], ['alfa']
        '''''

        data = self._data[data_names[0]].copy()
        nan_ind = np.isnan(data)
        data[nan_ind] = self._data[data_names[1]][nan_ind]
        self._data[new_data_name] = data

    def joint_hist_avg(self,param,by=None,new_data_name=None):
        # by = 'ae_centers'
        if not new_data_name: new_data_name = param
        if not by: 
            by = list(self._hist_axes[param].keys())[-1]
            ind = -1
        else:
            ind = list(self._hist_axes[param].keys()).index(by) -2
        centers = self._hist_axes[param][by]['centers']

        data = np.moveaxis(self._data[param], ind,-1)

        counts = np.nansum(data,axis=(-2,-1))
        result = np.nansum(data*centers,axis=(-2,-1))/counts

        self._data[new_data_name] = result

    def get_region_hist(self,param,region_ranges,density=True):
        index_arrays = self.get_region_index_array(region_ranges)
        data = self._data[param][index_arrays]
        axes = tuple([i for i in range(len(self._axis_names))])
        hist = np.nansum(data,axis=axes)
        if density: hist = hist/np.nansum(hist)
        return hist

    def plot_hist(self,param,region_ranges,xname,yname,density=True,bounds=None,ax=None,cmap='Reds',colorbar=True,**kwargs):
        
        data = self.get_region_hist(param,region_ranges,density)

        x_centers = self._hist_axes[param][xname]['centers']
        y_centers = self._hist_axes[param][yname]['centers']

        if data.shape != (len(y_centers),len(x_centers)):
            data = data.T

        if not ax: fig, ax = plt.subplots()
        norm = mcolors.BoundaryNorm(bounds, ncolors=256) if bounds else None

        pcm = ax.pcolormesh(x_centers,y_centers,data,cmap=cmap,norm=norm)
        if colorbar: plt.colorbar(pcm,ax=ax,extend='both')

        ax_set(ax,legend=False,**kwargs)
        return pcm







        
    