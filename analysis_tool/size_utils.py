import numpy as np
from scipy import interpolate

def cal_bin_centers(bin_num,size_ranges):
    """ Compute bin centers given the number of bins, maximum and minimum size """
    bin_width = (np.log(size_ranges[1])-np.log(size_ranges[0]))/(bin_num)
    finer_bound = [size_ranges[0]]
    for i in range(bin_num):
        finer_bound.append(np.exp(np.log(size_ranges[0])+(i+1)*bin_width))
    finer_centers = [(finer_bound[i+1]+finer_bound[i])/4*1.0E6 for i in range(len(finer_bound)-1)]
    return finer_centers

def map_bin_values(val_orig, bin_centers_orig, bin_centers_new):
    """ Map bin-type size distributions (dN or dV) on another size grid """
    finer_centers_log = [np.log(bd) for bd in bin_centers_new] 
    orig_centers_log = [np.log(bd) for bd in bin_centers_orig]
    
    if finer_centers_log[0] < orig_centers_log[0]:
        orig_centers_log.insert(0,finer_centers_log[0])
        val_orig.insert(0,0.0)
        
    if finer_centers_log[-1] > orig_centers_log[-1]:
        orig_centers_log.append(finer_centers_log[-1])
        val_orig.append(0.0)        

    f = interpolate.interp1d(orig_centers_log, val_orig)
    
    val_mapped=f(finer_centers_log)
    
    return val_mapped

def map_modal_values(self, val_orig, diam_orig, sigma_orig, bin_centers_new):
    """ Map modal-type size distributions on a sectional size grid """
    pass

class TypeSizeInfo():
    """
        class TypeSizeInfo:
            This class stores the size settings of an aerosol type.

            Parameters:

            - aerosol_name : Name of aerosols
            - filename     : Filename, e.g. dudvs, dudnt
            - size_type    : Size type, either 'bin' or 'modal'
            - modal_diam   : Modal diameter. Required if size_type='modal'
            - modal_sigma  : Modal standard deviation. Required if size_type='modal'
            - bin_num      : Number of bins. Required if size_type='bin'
            - bin_range    : Bin size range. Required if size_type='bin'
            - bin_centers  : Center of each bins 


    """
    def __init__(self,
                aerosol_name, filename,
                size_type, 
                modal_diam  = 1e-6,
                modal_sigma = 2.0,
                bin_num = 10, 
                bin_range = [3e-9, 10e-5]):

        self._aerosol_name = aerosol_name
        self._filename     = filename
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

    def get_filename(self):
        return self._filename
    
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

    def map_values(self,val_orig,bin_centers_new):
        if self._size_type == 'bin':
            return map_bin_values(val_orig,self._bin_centers,bin_centers_new)
        else:
            return map_modal_values(val_orig,self._modal_diam,self._modal_sigma,bin_centers_new)

