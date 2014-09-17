
from . import *

class View(Entity):
    
    objid_prefix = 'viw'
    geo_types = ['Point','MultiPoint','Line','MultiLine','Polygon','MultiPolygon']
    
    def geo_columns(self):
        """Get columns of any geographic type in the relation."""
        return [x for x in self.columns() if x['datatype'] in self.geo_types]

    def get_q_cols(self,select):
        raise NotImplementedError
        
    def columns(self):
        raise NotImplementedError
        
    def column(self,name):
        """Get a specific column by name."""
        for x in self.columns():
            if x['name'] == name:
                return x
        

