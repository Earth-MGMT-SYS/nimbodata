"""Module implements select PostgreSQL numeric datatypes."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from . import PG_Datatype as Datatype

try:
    import common.datatypes.numeric as num
except ImportError:
    import nimbodata.common.datatypes.numeric as num

class Boolean(num.Boolean,Datatype):
    
    def sql_create(self):
        return 'boolean'

class Integer(num.Integer,Datatype):
    
    def sql_create(self):
        return 'integer'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_Integer"("%(col)s") ''' % {
            'col':col
        }, {}
        
    def sql_target(self,colspec):
        if 'viewcolid' in colspec:
            viewcol = colspec['viewcolid']
        else:
            viewcol = None
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_Integer"("%(col)s") AS "%(viewcol)s" ''' % {
            'col':col,
            'viewcol':viewcol if viewcol is not None else col
        }, {}

class Float(num.Float,Datatype):
        
    def sql_create(self):
        return 'float'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_Float"("%(col)s") ''' % {
            'col':col
        }, {}

    def sql_target(self,colspec):
        if 'viewcolid' in colspec:
            viewcol = colspec['viewcolid']
        else:
            viewcol = None
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_Float"("%(col)s") AS "%(viewcol)s" ''' % {
            'col':col,
            'viewcol':viewcol if viewcol is not None else col
        }, {}
