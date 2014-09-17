"""Module implements the prototype of a Nimbodata PostgreSQL Datatype."""
# Copyright (C) 2014  Bradley Alan Smith

import psycopg2.extensions

from . import Datatype

class PG_Datatype(Datatype):
    """The base class for a PostgreSQL datatype in Nimbodata.
    
    A datatype represents a datatype that can be stored in the database and 
    used on the platform.  Encapsulates the SQL for creating, the SQL for
    selecting a column of the type as a target, as well as functions for
    converting to/from JSON, as well as instantiation of complex platform types
    (such as geographic via Shapely).
    
    """
    
    sql_create = None
    
    def sql_target(self,colid,colname,alias=True):
        """Get the SQL statement to process a column in a Select target.
        
        Given a column objid and column name, returns the SQL text to
        properly format and alias the query results for the column.
        
        """
        if alias:
            return ''' "%(colid)s" AS "%(colname)s" ''' % {
                'colid':colid,
                'colname':colname
            }
        else:
            return ''' "%(colid)s" ''' % {
                'colid':colid
            }
    
