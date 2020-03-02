import os
import numpy as np
from py3grads import Grads
from analysis_utils import lon180,lon360

class GradsWrapper():
    def __init__(self,verbose=False,print=False):
        self._ga = Grads(verbose=verbose)
        self._files = []
        self._definitions = {}
        self._print = print
        self._maxlon = 360

        self._ga('set gxout print')
        
    def get_ga(self):
        return self._ga
    
    def get_files(self):
        return self._files

    def get_definitions(self):
        return self._definitions

    def set_print(self,value):
        self._print = value

    def set_maxlon(self,value):
        self._maxlon = value
    
    #
    def ga_run(self,cmd):
        if self._print: print(cmd)
        return self._ga(cmd)

    def ga_exp(self,var,op=''):
        if self._print: print('ga.exp: {}'.format(var+op))
        if op: 
            self.define('temp',var+op)
            return self._ga.exp('temp')
        else:
            return self._ga.exp(var+op)

    # Basic functions
    def open(self,filedir,var):
        filepath = os.path.join(filedir,var)
        self.ga_run('open '+filepath)
        # var = self.query(len(self._files)+1)[-2].split()[0]
        self._files.append(var)

    def close(self):
        self.ga_run('close {}'.format(len(self._files)))
        self._files.pop()

    def close_all(self):
        while self._files:
            self.close()

    def reinit(self):
        self.ga_run('reinit')

    def correct_lon(self,lon):
        return lon360(lon) if self._maxlon==360 else lon180(lon)

    def lon(self,lon,lon2=''):
        lon = self.correct_lon(lon)
        if lon2: lon2 = self.correct_lon(lon2)

        out,_ = self.ga_run('set lon {} {}'.format(lon,lon2))
        res = [float(x) for x in out[0].split()[-2:]]
        return res if lon2 else res[0]
    
    def lat(self,lat,lat2=''):
        out,_ = self.ga_run('set lat {} {}'.format(lat,lat2))
        res = [float(x) for x in out[0].split()[-2:]]
        return res if lat2 else res[0]

    def zlevel(self,z,z2=''):
        out,_ = self.ga_run('set z {} {}'.format(z,z2))
        return

    def time(self,t,t2=''):
        return self.ga_run('set t {} {}'.format(t,t2))

    def query(self,ind):
        out, _ = self.ga_run('query file {}'.format(ind))
        return out

    def define(self,left,right):
        self._definitions[left] = right
        return self.ga_run('define {}={}'.format(left,right))

    def display(self,var,op=''):
        return self.ga_run('d {}{}'.format(self.get_varname(var,op)))

    def tave(self,var,trange,op=''):
        return self.ga_run('d ave({}{},t={},t={})'.format(self.get_varname(var),op,trange[0],trange[1]))

    def tave_grid(self,var,trange,op=''):
        return self.ga_exp('ave({}{},t={},t={})'.format(self.get_varname(var),op,trange[0],trange[1]))

    def aave(self,var,trange=None,x=[0,360],y=[-90,90],op=''):
        pass

    def tloop(self,var,trange=None,**kwargs):
        if trange:
            self.time(trange[0],trange[1])
        return self.ga_exp(self.get_varname(var),**kwargs)
    
    # variable names
    def get_varname(self,var):
        if var in self._definitions: return var

        if type(var) == int:
            var = self._files[var-1] + '.' + str(var)
        elif var in self._files: # Not a composite varname
            var = var + '.' + str(self._files.index(var)+1)

        return var

    ###
    def locate(self,lat,lon):
        return self.lat(lat), self.lon(lon)

    def get_single_point(self,var,lat,lon,t=1,trange=None,zrange=None,**kwargs):
        
        self.locate(lat,lon)
        
        if trange:
            try:
                if zrange:
                    self.zlevel(zrange[0],zrange[1])
                    out = ' '.join(self.tave(var,trange,**kwargs)[0][2:-1])
                    return np.array([float(x) for x in out.split()])
                else:
                    return float(self.tave(var,trange,**kwargs)[0][-2].split()[-1])
            except:
                print('Error in get_single_point')
                print('Output from Grads:')
                print(self.tave(var,trange))
        else: # Snapshot
            self.time(t)
            try:
                return float(self.display(var,**kwargs)[0][0].split()[-1])
            except:
                print('Error in get_single_point')
                print('Output from Grads:')
                print(self.display(var)[0])
        
    def tave_exp(self,var,trange,op=''):
        self.ga_run('define x=ave({}{},t={},t={})'.format(self.get_varname(var),op,trange[0],trange[1]))
        return self.ga_exp('x')