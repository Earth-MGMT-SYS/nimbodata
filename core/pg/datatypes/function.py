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

    def sql_exp(self,*args):
        """Convert a tuple or list describing a Nimbodata expression to SQL."""
        if len(args) == 2:
            funcname = casts[args[0]]
            colid = args[1]
            return ''' "%(funcname)s"("%(colid)s") ''' % {
                'colid':colid,
                'funcname':funcname
            }
        elif len(args) == 3:
            print args
            funcname = casts[args[0]]
            col_a = args[1]
            col_b = args[2]
            if 'Point' in args: # This awaits an evolution and mild refactor.
                return """
                    ST_SetSRID(ST_Point("%(col_a)s","%(col_b)s"),4326)
                """ % {
                    'col_a':col_a,
                    'col_b':col_b,
                }
            
            return ''' %(funcname)s("%(col_a)s","%(col_b)s") ''' % {
                'col_a':col_a,
                'col_b':col_b,
                'funcname':funcname
            }
        
        
