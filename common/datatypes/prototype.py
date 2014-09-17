"""Module implements the prototype of a Nimbodata PostgreSQL Datatype."""
# Copyright (C) 2014  Bradley Alan Smith

import psycopg2.extensions

class Datatype(object):
    """The base class for a PostgreSQL datatype in Nimbodata.
    
    A datatype represents a datatype that can be stored in the database and 
    used on the platform.  Encapsulates the SQL for creating, the SQL for
    selecting a column of the type as a target, as well as functions for
    converting to/from JSON, as well as instantiation of complex platform types
    (such as geographic via Shapely).
    
    """
    
    @property
    def objid(self):
        """For serialization and identification."""
        return 'datatype:'+str(type(self).__name__)
        
    @property
    def info(self):
        """For serialization and identification."""
        return 'datatype:'+str(type(self).__name__)
    
    def __call__(self,*args,**kwargs):
        """Supports the idiom of using the object as identifier and factory.
        
        Points to `self.from_literal` and allows the idiom of column
        declaration and value instantiation from the same object.
        
        """
        return self.from_literal(*args,**kwargs)
    
    def from_literal(self,*args,**kwargs):
        """Instantiates the value from parameters provided."""
        raise NotImplementedError
    
