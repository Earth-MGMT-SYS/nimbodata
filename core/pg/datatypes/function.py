"""Module implements column-functions in PostgreSQL."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *
from . import PG_Datatype as Datatype
import common.datatypes.function as func

class Function(func.Function,Datatype):
    """A column function in PostgreSQL implemented in Nimbodata."""
    
    def sql_target(self,colid,funcname):
        return ''' "%(funcname)s"("%(colid)s") ''' % {
            'colid':colid,
            'funcname':funcname
        }
