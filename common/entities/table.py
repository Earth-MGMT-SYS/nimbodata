
from . import *

class Table(view.View):
    
    objid_prefix = 'tbl'

    def _start_colindex(self):
        raise NotImplementedError
        
    def add_columns(self,cols):
        raise NotImplementedError
    
    def insert(self,values,rowid=None):
        raise NotImplementedError
        
    def update(self,tblid,rowid,new_values):
        raise NotImplementedError
