from point_data import PointData
from analysis_utils import day_to_date, draw_progress_bar
import pandas as pd
import numpy as np
import datetime

site_rename_columns = {'Site':'Site name',
                       'Elevation':'Altitude',
                       'StartDate':'Start date',
                       'EndDate':'End date'}

class ImproveData(PointData):

    def __init__(self):
        PointData.__init__(self)
        self._avg_by = 'Code'

    def read_improve_xls(self,filename,path='',undef=-999):
        # Site information
        
        self._site_info = (pd.read_excel(path+filename,sheet_name='Sites')
                             .rename(columns=site_rename_columns))

        
        self._all_data = (pd.read_excel(path+filename,sheet_name='Data')
                            .merge(self._site_info[['Site name','Code']],how='left',left_on=['SiteCode'],right_on=['Code'])
                            .drop(columns=['SiteCode','Dataset','POC'])
                            .replace(-999,np.nan))

        self._site_info = self._site_info.set_index('Code')
        for date in ['Start date','End date']:
            self._site_info[date] = self._site_info.apply(lambda x:datetime.datetime.strptime(x[date],'%m/%d/%Y'),axis=1)

        return


# def improve_model_series(model_name,improve_name):
#     series =  {f'Orig ({model_name}) ':model_avg_orig[model_name],
#             f'Bin: {model_name})':model_avg_bin[model_name],
#             f'IMPROVE: {improve_name}':improve_avg[(f'{improve_name}:Value', 'mean')]}
#     model_labels = list(series.keys())[:2]
#     obs_labels = list(series.keys())[2:]
#     return series, model_labels,obs_labels

# pairs = [['scont_sfc','SO4f'],['sacont_sfc','SeaSaltf'],['ccont_sfc','OCf'],['bccont_sfc','ECf']]
# for pair in pairs:
#     series,model_labels,obs_labels = improve_model_series(pair[0],pair[1])
#     print(obs_labels)