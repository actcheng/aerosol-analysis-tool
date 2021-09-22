import numpy as np
import pandas as pd
import datetime

from size_utils import cal_bin_centers
from type_size_info import TypeSizeInfo
from model_point_data import ModelPointData

MERGE_COL = ['Site name','Start date']
SORT_COL = 'Site name'
def merge(merged, data):
    if merged is None:
        return data
    else:
        return merged.merge(data,left_index=True,right_index=True, on=MERGE_COL)

class ModelPointSizeData(ModelPointData,TypeSizeInfo):
    """

    """
    def __init__(self, type_info_list=None, 
                 bin_num = 10, bin_range = [3e-9, 10e-5],**kwargs):

        ModelPointData.__init__(self)
        TypeSizeInfo.__init__(self,'Total','tt','bin',
                              bin_num=bin_num,bin_range=bin_range,**kwargs)

        if type_info_list is not None:
            self.type_info = type_info_list 

    @property
    def type_info(self):
        return self._type_info

    @type_info.setter
    def type_info(self, type_info_list):
        self._type_info = type_info_list and {t.aerosol_name: t for t in type_info_list}

    def get_grads_all_from_info(self, grads_dir, show_progress=True, cal_total=True, to_dlnr=False,to_dlogr=False,extra_var=[],*args, **kwargs):

        merged = None
        
        for var in extra_var:
            print('Read ', var)
            all = self.read_grads_all(grads_dir, [var], *args,show_progress=show_progress,**kwargs)
            merged = merge(merged, all)

        for key in self._type_info:
            t = self._type_info[key]
            if show_progress: print(f'\nRead {t.aerosol_name} data')

            all = self.read_grads_all(grads_dir, [t.var_name], *args,zrange=[1,t.bin_num],show_progress=show_progress,**kwargs)
            merged = merge(merged, all)

        # merged
        if cal_total:
            df_avg = self.get_total_size_dist()
            
        return merged

    def get_grads_avg_from_info(self,grads_dir, type='mean',# Mean, median
                                 cal_total=True,                                 
                                 cal_centers_from_num=False,
                                 to_dlnr=False,
                                 to_dlogr=False,
                                 show_progress=True,
                                 *args, **kwargs):

        df_avg = self._site_info.copy()

        for key in self._type_info:
            t = self._type_info[key]
            if show_progress: print(f'\nRead {t.aerosol_name} data')
            if type == 'median':
                start_dates = [datetime.datetime.now()] # Dummy
                avg = self.get_grads_median(grads_dir,[t.var_name],start_dates,zrange=[1,t.bin_num],**kwargs)
            else:
                avg = self.get_grads_avg(grads_dir,[t.var_name],*args,zrange=[1,t.bin_num],show_progress=show_progress,**kwargs) 

            if cal_centers_from_num:
                avg_num = self.get_grads_avg(grads_dir,[t.var_num_name],*args,zrange=[1,t.bin_num],**kwargs)
                dens = t.density # Should not be considered in new output
                centers = (avg.values[:,2:]/avg_num.values[:,2:]/(dens*np.pi/6))**(1/3)*1e6
            else:
                centers = np.array([t.bin_centers]*len(avg))
            
            avg_centers = pd.DataFrame(np.array(centers),columns=t.centerlist,index=avg.index)    

            if to_dlnr:
                dlnr = np.log(t.bin_centers[1]/2)-np.log(t.bin_centers[0]/2)
                # dens = t.density # Should not be considered in new output
                avg = avg/dlnr #*1.0E6/dens
            elif to_dlogr:
                dlogr = np.log10(t.bin_centers[1]/2)-np.log10(t.bin_centers[0]/2) 
                avg = avg/dlogr

            site_df = (avg[t.varlist].merge(avg_centers,left_index=True,right_index=True) 
                        if cal_centers_from_num 
                        else avg[t.varlist] )
            df_avg = df_avg.merge(site_df,left_index=True,right_index=True)
                

        self._avg_data = df_avg

        if cal_total:
            df_avg = self.get_total_size_dist()
            self._avg_data = df_avg

        return df_avg

    def get_total_size_dist(self): 
        def map_row_values(row):
            total =  np.zeros((self._bin_num,))
            for key in self._type_info:
                t = self._type_info[key]
                if t.centerlist[0] in row.index:
                    mapped = self.map_values(list(row[t.varlist].values),list(row[t.centerlist].values))
                else:
                    mapped = self.map_values(list(row[t.varlist].values),t.bin_centers) 
                total += mapped
            return total
        
        df_total = pd.DataFrame(self._avg_data.apply(lambda x: map_row_values(x),axis=1)        
                                .values.tolist(), 
                                columns=self.varlist,
                                index=self._avg_data.index)
        
        return (self._avg_data.drop(columns=self.varlist,errors='ignore')
                 .merge(df_total,left_index=True,right_index=True))
        
    def set_avg_to_all(self):
        self._all_data = self._avg_data.reset_index()    

    def partition_sum(self,cutoff=None,cutoff_column=[],cutoff_scale=1e3):
        """ Calculate the sum with size below and above boundary """
        if not cutoff_column and not cutoff: 
            print('Mush either provide a cutoff value/column!')
            return

        def summation(row):
            left, right = [],[]
            if cutoff_column: 
                cutoff_val = list(row[cutoff_column])[0] / cutoff_scale 
            else:
                cutoff_val = cutoff

            for t in self._type_info:
                left.append(0)
                right.append(0)
                centers = t.bin_centers
                for i, col in enumerate(t.varlist):
                    if centers[i] < cutoff_val:
                        left[-1] += row[col]
                    else:
                        right[-1] += row[col]

            return [sum(left),sum(right)] + left + right

        columns = ['left','right'] + [f'{side}.{t.var_prefix}' for side in ['left', 'right'] for t in self._type_info]
        df_part = pd.DataFrame(self._avg_data.apply(lambda x: summation(x),axis=1)
                                   .values.tolist(),
                                columns=columns,
                                index=self._avg_data.index)
        return self._site_info.merge(df_part,left_index=True,right_index=True)
    
