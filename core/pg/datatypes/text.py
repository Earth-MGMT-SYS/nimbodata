"""Module implements text types."""
# Copyright (C) 2014  Bradley Alan Smith

import json

from . import *
from . import PG_Datatype as Datatype

import common.datatypes.text as txt

def fallback_json(obj):
    return obj.objid

class Text(txt.Text,Datatype):
    
    def sql_create(self):
        return 'text'
        
class Json(txt.Json,Datatype):
    
    def sql_create(self):
        return 'json'
