from size_utils import cal_bin_centers
from type_size_info import TypeSizeInfo
from model_point_data import ModelPointData

class ModelPointSizeData(ModelPointData,TypeSizeInfo):
    """

    """
    def __init__(self, type_info_list=None, 
                 bin_num = 100, bin_range = [3e-9, 10e-5]):

        ModelPointData.__init__(self)
        TypeSizeInfo.__init__(self,'Total','tt','bin',
                              bin_num=bin_num,bin_range=bin_range)

        self._type_info = type_info_list

    def get_type_info(self):
        return self._type_info

    def set_type_info(self, type_info_list):
        self._type_info = type_info_list
        
    def get_grads_avg_from_info(self,grads_dir,cal_total=True,
                                 *args, **kwargs):

        df_avg = self._site_info.copy()

        for t in self._type_info:
            avg = self.get_grads_avg(grads_dir,[t.get_var_name()],*args,zrange=[1,t.get_bin_num()],**kwargs)
            df_avg = df_avg.merge(avg[t.get_varlist()],left_index=True,right_index=True)
        return df_avg

    def get_total_size_dist(self):
        pass

    def partition_size(self,boundary):
        """ Partition  """
        pass
    
         
