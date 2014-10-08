"""Module implements date and time types."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from . import PG_Datatype as Datatype

import common.datatypes.time as base_time

class Date(base_time.Date,Datatype):
    
    def sql_create(self):
        return 'date'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        fmt = colspec['args'][1]
        return ''' to_date("%(col)s", %(fmt)s ) ''' % {
            'col':col,
            'fmt':'%(fmt)s'
        }, {'fmt':fmt}


class Timestamp(base_time.Timestamp,Datatype):
    
    def sql_create(self):
        return 'timestamp'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        fmt = colspec['args'][1]
        return ''' to_timestamp("%(col)s", %(fmt)s ):: timestamp ''' % {
            'col':col,
            'fmt':'%(fmt)s'
        }, {'fmt':fmt}


class Time(base_time.Timestamp,Datatype):
    
    def sql_create(self):
        return 'time'
    
    def sql_cast(self,colspec):
        raise NotImplementedError
