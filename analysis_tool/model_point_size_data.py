import numpy as np
import pandas as pd

from size_utils import cal_bin_centers
from type_size_info import TypeSizeInfo
from model_point_data import ModelPointData

class ModelPointSizeData(ModelPointData,TypeSizeInfo):
    """

    """
    def __init__(self, type_info_list=None, 
                 bin_num = 10, bin_range = [3e-9, 10e-5],**kwargs):

        ModelPointData.__init__(self)
        TypeSizeInfo.__init__(self,'Total','tt','bin',
                              bin_num=bin_num,bin_range=bin_range,**kwargs)

        self._type_info = type_info_list and {t.get_aerosol_name(): t for t in type_info_list} 

    def get_type_info(self):
        return self._type_info

    def set_type_info(self, type_info_list):
        self._type_info = type_info_list and {t.get_aerosol_name(): t for t in type_info_list}

    def get_grads_avg_from_info(self,grads_dir,cal_total=True,
                                 mass_to_volume=False,
                                 to_dlogr=False,
                                 *args, **kwargs):

        df_avg = self._site_info.copy()

        for key in self._type_info:
            t = self._type_info[key]
            print(f'\nRead {t.get_aerosol_name()} data')
            avg = self.get_grads_avg(grads_dir,[t.get_var_name()],*args,zrange=[1,t.get_bin_num()],**kwargs)
            if mass_to_volume:
                dlnr = np.log(t.get_bin_centers()[1]/2)-np.log(t.get_bin_centers()[0]/2)
                dens = t.get_density()
                avg = avg*1.0E6/dens/dlnr
            elif to_dlogr:
                dlogr = np.log10(t.get_bin_centers()[1]/2)-np.log10(t.get_bin_centers()[0]/2) 
                avg = avg/dlogr
            df_avg = df_avg.merge(avg[t.get_varlist()],left_index=True,right_index=True)

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
                mapped = self.map_values(list(row[t.get_varlist()].values),t.get_bin_centers())
                total += mapped
            return total
        
        df_total = pd.DataFrame(self._avg_data.apply(lambda x: map_row_values(x),axis=1)        
                                .values.tolist(), 
                                columns=self.get_varlist(),
                                index=self._avg_data.index)
        
        return (self._avg_data.drop(columns=self.get_varlist(),errors='ignore')
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
                centers = t.get_bin_centers()
                for i, col in enumerate(t.get_varlist()):
                    if centers[i] < cutoff_val:
                        left[-1] += row[col]
                    else:
                        right[-1] += row[col]

            return [sum(left),sum(right)] + left + right

        columns = ['left','right'] + [f'{side}.{t.get_var_prefix()}' for side in ['left', 'right'] for t in self._type_info]
        df_part = pd.DataFrame(self._avg_data.apply(lambda x: summation(x),axis=1)
                                   .values.tolist(),
                                columns=columns,
                                index=self._avg_data.index)
        return self._site_info.merge(df_part,left_index=True,right_index=True)
    
