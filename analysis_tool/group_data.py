from base_data import Data

class GroupData(Data):
    def __init__(self,info=None,**kwargs):
        Data.__init__(self)
        if info != None: 
            self.set_info(info,**kwargs)

    def set_info(self,info,by='Site name'):
        self._info = info
        self._keys = list(info.keys())
        self._groupbys = {key:info[key]['data'].get_all_data().groupby(by)
                            for key in self._keys}
        self._groupnames = list(self._groupbys[self._keys[0]].groups.keys())
        self._styles = {key:info[key]['style'] for key in self._keys}

    def get_info(self):
        return self._info

    def get_keys(self):
        return self._keys
    
    def get_groupbys(self):
        return self._groupbys

    def get_groupnames(self):
        return self._groupnames

    def get_styles(self):
        return self._styles

    def set_styles(self,key,param,value):
        self._style[key][param] = value