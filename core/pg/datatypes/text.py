"""Module implements text types."""
# Copyright (C) 2014  Bradley Alan Smith

import json

from . import *
from . import PG_Datatype as Datatype

try:
    import common.datatypes.text as txt
except ImportError:
    import nimbodata.common.datatypes.text as txt

def fallback_json(obj):
    return obj.objid

class Text(txt.Text,Datatype):
    
    def sql_create(self):
        return 'text'
        
    def sql_cast(self,colspec):
        col = colspec['args'][0]
        return ''' "_adm-registries"."to_Text"("%(col)s") ''' % {
            'col':col
        }, {}
        
class Json(txt.Json,Datatype):
    
    def sql_create(self):
        return 'json'
