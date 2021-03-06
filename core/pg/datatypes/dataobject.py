"""Module implements text types."""
# Copyright (C) 2014  Bradley Alan Smith

import json

from . import *
from . import PG_Datatype as Datatype

try:
    import common.datatypes.dataobject as obj
except ImportError:
    import nimbodata.common.datatypes.dataobject as obj
        
class DataObject(obj.DataObject,Datatype):
    
    def sql_create(self):
        return 'jsonb'
