"""Module implements time expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class TimeFunction(base.TimeFunction):
    """Base class for any math function in PostgreSQL."""
    
    def sql_target(self,colid,param,newcolid):
        if param not in self.fields:
            raise ValueError('Invalid time field ' + param)
        return ''' %(func)s(%(param)s FROM "%(colid)s") AS "%(newcolid)s" ''' % {
            'colid':colid,
            'func': type(self).__name__.lower(),
            'param':param,
            'newcolid':newcolid if newcolid is not None else colid
        }
    
    def sql_cast(self,colid,param):
        if param not in self.fields:
            raise ValueError('Invalid time field ' + param)
        return ''' %(func)s(%(param)s FROM "%(colid)s") ''' % {
            'colid':colid,
            'func': type(self).__name__.lower(),
            'param':param
        }

# CONSTANTS/OTHER


# VALUE
class extract(base.extract,TimeFunction):
    """Gets the absolute value of a value.""" 

