"""Module implements column-functions in PostgreSQL."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from . import PG_Datatype as Datatype
import common.datatypes.function as func

class Function(func.Function,Datatype):
    """A Nimbodata function is an abstraction of a database function."""
    
    def sql_target(self,colid,funcname):
        """Simple statement for use as basic target."""
        return ''' "%(funcname)s"("%(colid)s") AS "%(colid)s" ''' % {
            'colid':colid,
            'funcname':funcname
        }
        
