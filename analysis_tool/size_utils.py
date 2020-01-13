import numpy as np
from scipy import interpolate

def cal_bin_centers(bin_num,size_ranges):
    """ Compute bin centers given the number of bins, maximum and minimum size """
    bin_width = (np.log(size_ranges[1])-np.log(size_ranges[0]))/(bin_num)
    finer_bound = [size_ranges[0]*1.0E6 ]
    for i in range(bin_num):
        finer_bound.append(np.exp(np.log(size_ranges[0])+(i+1)*bin_width)*1.0E6 )
    finer_centers = [(finer_bound[i+1]+finer_bound[i])/2 for i in range(len(finer_bound)-1)]
    return finer_centers, finer_bound

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

def map_modal_values(val_orig, diam_orig, sigma_orig, bin_centers_new):
    """ Map modal-type size distributions on a sectional size grid """
    return bin_centers_new

