"""Module implements postgresql range datatypes in Nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from . import PG_Datatype as Datatype

try:
    import common.datatypes.ranges as base_range
except ImportError:
    import nimbodata.common.datatypes.ranges as base_range

class IntegerRange(base_range.IntegerRange,Datatype):
    
    sql_create = 'int4range'

class LongRange(base_range.LongRange,Datatype):
    
    sql_create = 'int8range'

class FloatRange(base_range.FloatRange,Datatype):
    
    sql_create = 'numrange'

class RangeAdapter(object):
    
    def __init__(self,f):
        self._f = f
    
    def getquoted(self):
        return "'%(val)s'::%(typ)s" % {
            'val':self._f.value,
            'typ':self._f.sql_create
        }
    
    @staticmethod
    def cast(s, cur):
        if s is None:
            return None
        else:
            return s

