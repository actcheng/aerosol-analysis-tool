import datetime

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

def day_to_date(start_date,days):
    return start_date + datetime.timedelta(float(days))

def filter_time(df,col='',period=[],year=None,month=None):
    if not col: return df
    if period:
        return df[(df[col]>= period[0]) & (df[col] <= period[1])]
    elif year:
        return df[(df[col]>= datetime.datetime(year,1,1)) & (df[col] < datetime.datetime(year+1,1,1))] 
    elif month:
        df[(df[col].apply(lambda x: x.month==month))]
    else:
        return df

def remove_outlier(series_in):
    q1 = series_in.quantile(0.25)
    q3 = series_in.quantile(0.75)
    iqr = q3-q1 #Interquartile range
    fence_low  = max(0,q1-1.5*iqr)
    fence_high = q3+1.5*iqr
    series_out = series_in.mask(series_in>fence_high).mask(series_in<fence_low)
    return series_out

def lon360(lon180):
    return lon180 if lon180 > 0 else lon180 + 360

def lon180(lon360):
    return lon360 if lon360 <= 180 else lon360 - 360

def ax_selector(axes,irow,icol,nrows,ncols):
    if nrows==1:
        return axes[icol] if ncols>1 else axes
    elif ncols==1:
        return axes[irow] if nrows>1 else axes
    else:
        return axes[irow,icol]