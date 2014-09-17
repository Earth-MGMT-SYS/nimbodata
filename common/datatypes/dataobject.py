"""Module implements the prototype of a Nimbodata PostgreSQL Datatype."""
# Copyright (C) 2014  Bradley Alan Smith


import json
import psycopg2.extensions

from . import *

import common.comparable as comparable

comparable.operators += ['@>','<@','?','?|','?&']

class DataObject(Datatype):
    """The base class for a PostgreSQL datatype in Nimbodata.
    
    A datatype represents a datatype that can be stored in the database and 
    used on the platform.  Encapsulates the SQL for creating, the SQL for
    selecting a column of the type as a target, as well as functions for
    converting to/from JSON, as well as instantiation of complex platform types
    (such as geographic via Shapely).
    
    """
        
    def from_literal(self,value):
        return json.loads(value)

    def contains(self,this,other):
        return comparable.WhereClause(this['name'],'@>',other)
        
    def containedby(self,this,other):
        return comparable.WhereClause(this['name'],'<@',other)

    def haskey(self,this,other):
        return comparable.WhereClause(this['name'],'?',other)

    def hasall(self,this,other):
        return comparable.WhereClause(this['name'],'?&',other)
        
    def hasany(self,this,other):
        return comparable.WhereClause(this['name'],'?|',other)
        
