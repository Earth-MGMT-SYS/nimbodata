"""Module implements date and time types."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from . import PG_Datatype as Datatype

import common.datatypes.time as base_time

class Date(base_time.Date,Datatype):
    
    def sql_create(self):
        return 'date'

class Timestamp(base_time.Timestamp,Datatype):
    
    def sql_create(self):
        return 'timestamp'

class Time(base_time.Timestamp,Datatype):
    
    def sql_create(self):
        return 'time'
