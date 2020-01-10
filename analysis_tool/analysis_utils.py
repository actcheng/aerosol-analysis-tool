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

    # Statistics
    - remove_outlier

    # Geolocations
    - lon360
    - lon180
    
    # Plotting
    - ax_selector
    - ax_set

    # Output tool
    - draw_progress_bar
"""



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

## Geolocations
def lon360(lon180):
    return lon180 if lon180 > 0 else lon180 + 360

def lon180(lon360):
    return lon360 if lon360 <= 180 else lon360 - 360

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
    for attr in attrs:
        if attr in kwargs:
            getattr(ax,'set_'+attr)(kwargs[attr])

    if legend==True: ax.legend()
    plt.tight_layout()

    if savename: 
        full = add_suffix(savedir,'/') + savename.lower()+'_'+add_suffix(save_suffix.lower().replace(' ','_'),'.png')
        plt.savefig(full,dpi=200)
        print(f'Saved as {full}')

## Output tool
def draw_progress_bar(percent, bar_len = 50):
    import sys
    sys.stdout.write("\r")
    progress = ""
    for i in range(bar_len):
        if i < int(bar_len * percent):
            progress += "="
        else:
            progress += " "

    sys.stdout.write("[{:<{}}] {:.0f}%".format("=" * int(bar_len * percent), bar_len, percent * 100))
    sys.stdout.flush()

    return
