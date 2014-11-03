"""Module implements math expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class GeoFunction(base.GeoFunction):
    """Base class for any math function in PostgreSQL."""
    
    def sql_target(self,colid,*args):
        if len(args) == 1 and args[0] is not None:
            viewcol = args[0]
        elif len(args) == 2:
            tolerance = args[0]
            viewcol = args[1]
        else:
            viewcol = None
        return '''(ST_%(func)s("%(colid)s",%(tol)s)) AS "%(viewcol)s" ''' % {
            'colid':colid[0] + '"."' + colid[1],
            'func': type(self).__name__.title(),
            'viewcol': viewcol if viewcol is not None else colid,
            'tol':float(tolerance)
        }

# VALUE
class simplify(GeoFunction):
    """Gets the absolute value of a value.""" 
