"""
    This module contains utilities for analysis_tool.

    Utility list:

    # Text and files
    - add_suffix
    - get_filelist
    - get_filelist_from_dir
    - get_sites_from_filenames

    # Date and time
    - day_to_date
    - filter_time
    - dt64_to_dt

    # Dataframe
    - columns_first

    # Read grads
    - ga_read_ctl
    - ga_open_file

    # Statistics
    - remove_outlier
    - cal_bias
    - gammafunc

    # Geolocations
    - lon360
    - lon180
    - grid_area
    - bound_to_index

    # Plotting
    - ax_selector
    - ax_set
    - savefig

    # Output tool
    - draw_progress_bar
"""
import datetime
import numpy as np
import matplotlib.pyplot as plt

# Constants
LRTP     = 0.9189385332046727

## Text and files
def add_suffix(S,suf):
    return S + (suf if S[-(len(suf)):]!=suf else '')

def get_keyword(string,keywords):
    for keyword in keywords:
        if keyword in string: return keyword
        
def get_filelist(all_files,optional=[],required=[]):
    """ Return a list of filenames with the required keyword and one of the optional keywords"""
    return sorted([file 
            for file in all_files 
            if (not required or all([req in file for req in required])) and 
               (not optional or any([opt in file for opt in optional]))])

def get_filelist_from_dir(filedir,**kwargs):
    """ Return a list of filenames in file directory"""
    import os

    return get_filelist(os.listdir(filedir),**kwargs)

def get_sites_from_filenames(filelist,delimiter='_',loc=0):
    return set([filename.split(delimiter)[loc] for filename in filelist])

## Date and time
def day_to_date(start_date,days):
    import datetime

    return start_date + datetime.timedelta(float(days))

def hours_to_datelist(start_date,length):
    import datetime

    return [start_date + datetime.timedelta(hours=i) for i in range(1,length+1)]

def filter_time(df,col='',period=[],year=None,month=None):
    import datetime

    if not col: return df
    if period:
        return df[(df[col]>= period[0]) & (df[col] <= period[1])]
    elif year:
        return df[(df[col]>= datetime.datetime(year,1,1)) & (df[col] < datetime.datetime(year+1,1,1))] 
    elif month:
        df[(df[col].apply(lambda x: x.month==month))]
    else:
        return df

def dt64_to_dt(dt64):  
    return np.datetime64( dt64, 'us').astype(datetime.datetime)



## Dataframe
def columns_first(df,cols_f):
    cols = list(df.columns)
    cols_b = [col for col in cols if col not in cols_f]
    return  df[cols_f+cols_b]

## GrADS
def ga_open_file(ga,grads_dir,grads_name,check,i,file_suffixes,time_ranges):

    if len(time_ranges) > 1:
        if type(grads_dir) == list:
            ga.open(f'{grads_dir[i]}/{check}',grads_name)
        elif file_suffixes:
            ga.open(f'{grads_dir}_{file_suffixes[i]}/{check}',grads_name)
        else:
            ga.open(f'{grads_dir}_{i+1}/{check}',grads_name)
    else:
        ga.open(f'{grads_dir}/{check}',grads_name)  

def ga_read_ctl(ga,*args):
    ga_open_file(ga,*args)
    ctl=ga.ga_run('q ctlinfo')
    ga.close()
    ctl = [x for line in ctl[0] for x in line.split()]

    # Get lon
    start = ctl.index('xdef')
    nlon= int(ctl[start+1])
    lons = [float(x) for x in ctl[start+3:start+nlon+3]]

    # Get lat
    start = ctl.index('ydef')
    nlat = int(ctl[start+1])
    lats = [float(x) for x in ctl[start+3:start+nlat+3]]

    # Get zlevs
    start = ctl.index('zdef')
    nz = int(ctl[start+1])
    zlevs = [float(x) for x in ctl[start+3:start+nz+3]]

    return lats, lons, zlevs

## Statistics
def remove_outlier(series_in):
    q1 = series_in.quantile(0.25)
    q3 = series_in.quantile(0.75)
    iqr = q3-q1 #Interquartile range
    fence_low  = max(0,q1-1.5*iqr)
    fence_high = q3+1.5*iqr
    series_out = series_in.mask(series_in>fence_high).mask(series_in<fence_low)
    return series_out

def get_freq(data,**kwargs):
    import numpy as np

    hist = np.histogram(data,**kwargs)
    data = hist[0]/sum(hist[0])
    return data

def cal_bias(obs,model,bias_log=True):
    import numpy as np

    # diff = (model-obs)/obs
    diff = (np.log10(model)-np.log10(obs))/np.log10(obs) if bias_log else (model-obs)/obs 
    valid = len(model[~np.isnan(diff)])
    return np.nansum(diff)/valid

def gammafunc(x):
    dx = x - 1.0
    Ag = 0.999999999999809932276847004735 \
       + 676.520368121885098567009190444    / ( dx + 1.0 ) \
       - 1259.13921672240287047156078755    / ( dx + 2.0 ) \
       + 771.323428777653078848652825889    / ( dx + 3.0 ) \
       - 176.615029162140599065845513540    / ( dx + 4.0 ) \
       + 12.5073432786869048144589368533    / ( dx + 5.0 ) \
       - 0.138571095265720116895547069851   / ( dx + 6.0 ) \
       + 9.98436957801957085956266899569E-6 / ( dx + 7.0 ) \
       + 1.50563273514931155833835577539E-7 / ( dx + 8.0 )

    work = np.exp( LRTP + (dx+0.5)*np.log(dx+7.5) - (dx+7.5) + np.log(Ag) )
    return np.real(work)

## Geolocations
def lon360(lon180):
    return lon180 if lon180 > 0 else lon180 + 360

def lon180(lon360):
    return lon360 if lon360 <= 180 else lon360 - 360

def grid_area(lats,lons,radius=6371*1000):
    '''
    Calculate the grid area given the ranges of latitudes and longitudes
        lats: [lat1,lat2]
        lons: [lon1,lon2], area between lon1 and lon2
    '''
    from math import pi, sin
    lon_diff = (lons[1]-lons[0])/180*pi
    lat_diff = sin(lats[1]/180*pi)-sin(lats[0]/180*pi)
    if lon_diff < 0: lon_diff += 2*pi
    return radius**2*lat_diff*lon_diff

def bound_to_index(grid,bounds):
    '''
    Given a list of 1D points and upper & lower bounds, return the range of indices matching the condition

    Inputs:
    - grid: list of float (e.g. lons)
    - bounds: [lower, upper], where lower & upper are float 

    Return:
    - ranges: list of float (1 <= len(ranges) <= 2)
    '''

    low, up = min(bounds), max(bounds)

    low_ind,up_ind = sorted([search_index(grid,low), search_index(grid,up)])

    if bounds[0] < bounds[1]:
        return [[low_ind,up_ind]]
    else:
        return [[0,low_ind],[up_ind,len(grid)]]

def search_index(arr,val):
    '''Search for index with first value larger than value'''

    if arr[0] > arr[1]: # Reversed
        return len(arr) - search_index(arr[::-1],val) -1

    l, r = 0, len(arr)-1
    while l+1 < r:
        mid = (l+r) // 2
        if arr[mid] == val:
            return mid
        elif arr[mid] > val:
            r = mid
        else:
            l = mid
    return r if arr[l] < val else l
        


# Plotting
def ax_selector(axes,irow,icol,nrows,ncols):
    if nrows==1:
        return axes[icol] if ncols>1 else axes
    elif ncols==1:
        return axes[irow] if nrows>1 else axes
    else:
        return axes[irow,icol]

def ax_set(ax, 
            legend=True,
            save_suffix='',          
            savedir='',
            savename=None, **kwargs):
    
    import matplotlib.pyplot as plt 

    attrs = ['title','xlim','ylim','xlabel','ylabel','xscale','yscale']
    [getattr(ax,'set_'+attr)(kwargs[attr]) for attr in attrs if attr in kwargs]

    if legend==True: 
        ax.legend()
    # else:
    #     ax.legend().set_visible(False)
    plt.tight_layout()

    if savename: 
        full = add_suffix(savedir,'/') + savename.lower()+'_'+add_suffix(save_suffix.lower().replace(' ','_'),'.png')
        plt.savefig(full,dpi=200)
        print(f'Saved as {full}')

def savefig(savename,fig=None,dpi=200,**kwargs):
    if fig is None:
        plt.savefig(savename,dpi=dpi,**kwargs)
    else: 
        fig.savefig(savename,dpi=dpi,**kwargs)

    print(f'Saved as {savename}')

## Output tool
def draw_progress_bar(percent, show_progress=True, bar_len = 50):
    import sys
    sys.stdout.write("\r")
    filled_len = int(bar_len * percent)
    progress = "="*filled_len + " "*(bar_len-filled_len)
    sys.stdout.write("[{}] {:.0f}%".format(progress, percent * 100))
    # sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(bar_len * percent), bar_len, percent * 100))
    sys.stdout.flush()

    if percent == 1.:
        print('\n')
    return
