"""Module implements time expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class TimeFunction(base.TimeFunction):
    """Base class for any math function in PostgreSQL."""
    
    def sql_target(self,colid,param,newcolid):
        if param not in self.fields:
            raise ValueError('Invalid time field ' + param)
        
        if param == 'water_year':
            sqlstr =  '''
            "_adm-registries"."to_WaterYear"( "%(colid)s" ) AS "%(newcolid)s"
            '''
        else:
            sqlstr = '''
                %(func)s(%(param)s FROM "%(colid)s") AS "%(newcolid)s" 
            ''' 
        return sqlstr % {
            'colid':colid[0] + '"."' + colid[1],
            'func': type(self).__name__.lower(),
            'param':param,
            'newcolid':newcolid if newcolid is not None else colid[1]
        }
    
    def sql_cast(self,colid,param):
        print type(self).__name__.lower(), colid, param
        if param not in self.fields:
            raise ValueError('Invalid time field ' + param)
        if param == 'water_year':
            sqlstr =  '''
            "_adm-registries"."to_WaterYear"( "%(colid)s" )
            '''
        else:
            sqlstr = ''' %(func)s(%(param)s FROM "%(colid)s") '''
        return sqlstr % {
            'colid':colid,
            'func': type(self).__name__.lower(),
            'param':param
        }

# CONSTANTS/OTHER


# VALUE
class extract(base.extract,TimeFunction):
    """Gets the absolute value of a value."""

class now(base.now,TimeFunction):
    """The SQL Now"""
    
    def sql_target(self,*args,**kwargs):
        return """ now() """

    def sql_cast(self, *args, **kwargs):
        return """ now() """
