import numpy as np
from scipy import interpolate

from size_utils import cal_bin_centers, map_bin_values, map_modal_values

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
                var_type='dvt',
                var_num='dnt', # For calculating bin_centers
                density=1.0, **kwargs):

        self._aerosol_name = aerosol_name
        self._var_prefix   = var_prefix
        self._var_type     = var_type
        self._var_num      = var_num
        self._size_type    = size_type.lower()
        self._density      = density

        if self._size_type == 'modal':
            self._modal_diam = modal_diam
            self._modal_sigma = modal_sigma
        else:            
            self._bin_range = bin_range
            self._bin_centers, self._bin_bounds = cal_bin_centers(bin_num,bin_range)
            self.bin_num = bin_num

    # Access information
    @property
    def aerosol_name(self):
        return self._aerosol_name

    @property
    def var_prefix(self):
        return self._var_prefix
    
    @property
    def var_type(self):
        return self._var_type

    @var_type.setter
    def set_var_type(self,var_type):
        self._var_type = var_type
        self.set_varlist()

    @property
    def var_num(self):
        return self._var_num

    @property
    def var_name(self):
        return self._var_prefix + self._var_type

    @property
    def var_num_name(self):
        return self._var_prefix + self._var_num

    @property
    def size_type(self):
        return self._size_type

    @property
    def density(self):
        return self._density

    @property
    def modal_diam(self):
        return self._modal_diam if self._size_type=='modal' else None

    @property
    def modal_sigma(self):
        return self._modal_sigma if self._size_type=='modal' else None

    @property
    def bin_num(self):
        return self._bin_num if self._size_type=='bin' else None

    @bin_num.setter
    def bin_num(self,bin_num):
        self._bin_num = bin_num
        self.set_varlist()

    @property
    def bin_range(self):
        return self._bin_range if self._size_type=='bin' else None
    
    @property
    def bin_centers(self):
        return self._bin_centers if self._size_type=='bin' else None

    @bin_centers.setter
    def bin_centers(self,bin_centers):
        if len(bin_centers) == self._bin_num:
            self._bin_centers = bin_centers
        else:
            print('Inconsistent number of bins! bin_num={}, input_length={}'.format(self._bin_num,len(bin_centers)))

    @property
    def varlist(self):
        return self._varlist

    def set_varlist(self):
        self._varlist =  [f'{self.var_name}.{i+1}' for i in range(self._bin_num)]
        self._centerlist = [f'{self.var_name}.c.{i+1}' for i in range(self._bin_num)] 

    @property
    def centerlist(self):
        return self._centerlist    

    def map_values(self,val_orig,bin_centers_orig,modal_diam_orig=None,modal_sigma_orig=None, modal_peak_orig=None):
        if not modal_diam_orig:
            return map_bin_values(val_orig,bin_centers_orig,self._bin_centers)
        else:
            return map_modal_values(val_orig,modal_diam_orig,modal_sigma_orig,self._bin_centers)

