"""Module implements select PostgreSQL numeric datatypes."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from . import PG_Datatype as Datatype

try:
    import common.datatypes.array as arr
except ImportError:
    import nimbodata.common.datatypes.array as arr

class BooleanArray(arr.BooleanArray,Datatype):
    
    def sql_create(self):
        return 'boolean[]'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_BooleanArray"("%(col)s") ''' % {
            'col':col
        }, {}

class IntegerArray(arr.IntegerArray,Datatype):
    
    def sql_create(self):
        return 'integer[]'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_IntegerArray"("%(col)s") ''' % {
            'col':col
        }, {}

class FloatArray(arr.FloatArray,Datatype):
        
    def sql_create(self):
        return 'float[]'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_FloatArray"("%(col)s") ''' % {
            'col':col
        }, {}

class TextArray(arr.TextArray,Datatype):
        
    def sql_create(self):
        return 'text[]'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_TextArray"("%(col)s") ''' % {
            'col':col
        }, {}
