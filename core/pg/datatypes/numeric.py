"""Module implements select PostgreSQL numeric datatypes."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from . import PG_Datatype as Datatype

import common.datatypes.numeric as num

class Boolean(num.Boolean,Datatype):
    
    def sql_create(self):
        return 'boolean'

class Integer(num.Integer,Datatype):
    
    def sql_create(self):
        return 'integer'

class Float(num.Float,Datatype):
        
    def sql_create(self):
        return 'float'
