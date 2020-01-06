import numpy as np
from scipy import interpolate

from size_utils import cal_bin_centers, map_bin_values 

class TypeSizeInfo():
    """
        class TypeSizeInfo:
            This class stores the size settings of an aerosol type.

            Parameters:

            - aerosol_name : Name of aerosols
            - varname      : Variable name, e.g. dudvs, dudnt
            - size_type    : Size type, either 'bin' or 'modal'
            - modal_diam   : Modal diameter. Required if size_type='modal'
            - modal_sigma  : Modal standard deviation. Required if size_type='modal'
            - bin_num      : Number of bins. Required if size_type='bin'
            - bin_range    : Bin size range. Required if size_type='bin'
            - bin_centers  : Center of each bins 


    """
    def __init__(self,
                aerosol_name, var_prefix,
                size_type, 
                modal_diam  = 1e-6,
                modal_sigma = 2.0,
                bin_num = 10, 
                bin_range = [3e-9, 10e-5],
                var_type='dns'):

        self._aerosol_name = aerosol_name
        self._var_prefix   = var_prefix
        self._var_type     = var_type
        self._size_type    = size_type.lower()

        if self._size_type == 'modal':
            self._modal_diam = modal_diam
            self._modal_sigma = modal_sigma
        else:
            self._bin_num = bin_num
            self._bin_range = bin_range
            self._bin_centers = cal_bin_centers(bin_num,bin_range)

    # Access information
    def get_aerosol_name(self):
        return self._aerosol_name

    def get_var_prefix(self):
        return self._var_prefix
    
    def get_var_type(self):
        return self._var_type
    
    def set_var_type(self,var_type):
        self._var_type = var_type

    def get_var_name(self):
        return self._var_prefix + self._var_type

    def get_size_type(self):
        return self._size_type

    def get_modal_diam(self):
        return self._modal_diam if self._size_type=='modal' else None

    def get_modal_sigma(self):
        return self._modal_sigma if self._size_type=='modal' else None

    def get_bin_num(self):
        return self._bin_num if self._size_type=='bin' else None

    def get_bin_range(self):
        return self._bin_range if self._size_type=='bin' else None
    
    def get_bin_centers(self):
        return self._bin_centers if self._size_type=='bin' else None

    def set_bin_centers(self,bin_centers):
        if len(bin_centers) == self._bin_num:
            self._bin_centers = bin_centers
        else:
            print('Inconsistent number of bins! bin_num={}, input_length={}'.format(self._bin_num,len(bin_centers)))

    def gen_varlist(self):
        return [f'{self.get_var_name()}.{i+1}' for i in range(self._bin_num)]

    def map_values(self,val_orig,bin_centers_new):
        if self._size_type == 'bin':
            return map_bin_values(val_orig,self._bin_centers,bin_centers_new)
        else:
            return map_modal_values(val_orig,self._modal_diam,self._modal_sigma,bin_centers_new)

