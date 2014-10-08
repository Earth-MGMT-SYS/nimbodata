"""Module implements general expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class GeneralFunction(base.GeneralFunction):
    """Base class for any math function in PostgreSQL."""
    
    def sql_target(self,colid,*args):
        if len(args) == 1 and args[0] is not None:
            viewcol = args[0]
        else:
            viewcol = colid
        return ''' %(func)s("%(colid)s") AS "%(viewcol)s" ''' % {
            'colid':colid,
            'func': type(self).__name__.lower(),
            'viewcol':viewcol
        }

class unique(GeneralFunction):
    """Return the unique values for a scalar."""
    
    def sql_target(self,colid,*args):
        if len(args) == 1 and args[0] is not None:
            viewcol = args[0]
        else:
            viewcol = colid
        return ''' DISTINCT "%(colid)s" AS "%(viewcol)s" ''' % {
            'colid':colid,
            'func': type(self).__name__.lower(),
            'viewcol':viewcol
        }

class count(GeneralFunction):
    """Return the number of values in the scalar."""
