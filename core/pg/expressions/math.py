"""Module implements math expressions in select queries for nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class MathFunction(base.MathFunction):
    """Base class for any math function in PostgreSQL."""
    
    def sql_target(self,colid,*args):
        if len(args) == 1 and args[0] is not None:
            viewcol = args[0]
        else:
            viewcol = None
        return ''' %(func)s("%(colid)s") AS "%(viewcol)s" ''' % {
            'colid':colid[0] + '"."' + colid[1],
            'func': type(self).__name__.lower(),
            'viewcol': viewcol if viewcol is not None else colid
        }

class Constant(MathFunction):
    """Base class for any math function in PostgreSQL."""
    
    def sql_target(self,colid,*args):
        return ''' %(func)s() ''' % {
            'func':self.fname if self.fname is not None else \
                        type(self).__name__.lower()
        }


# Sometime I will come up with a smarter way to do this than copying all the
# classes and setting them to the implementation base... just not now.
# I could monkey patch sql_exp into the base class... I am tempted.

# CONSTANTS/OTHER
class pi(Constant):
    """Returns the pi constant."""
    
    def sql_exp(self,*args,**kwargs):
        return 'pi()'
        
class random(Constant):
    """Returns a random double precision between 0.0 and 1.0 inclusive."""
    
    def sql_exp(self,*args,**kwargs):
        return 'random()'
    

# SCALAR
class MAX(MathFunction):
    """Gets the max of a scalar."""

class AVG(MathFunction):
    """Gets the max of a scalar."""
        
class MIN(MathFunction):
    """Gets the max of a scalar."""
    
class SUM(MathFunction):
    """Gets the sum of a scalar."""


# VALUE
class ABS(MathFunction):
    """Gets the absolute value of a value.""" 

class cbrt(MathFunction):
    """Gets the cube root of a value."""
    
class ceiling(MathFunction):
    """Gets the ceiling of a value."""
    
class degrees(MathFunction):
    """Radians to degrees of a value."""
    
class exp(MathFunction):
    """Exponential of a value."""
    
class floor(MathFunction):
    """Gets the floor of a value."""
    
class ln(MathFunction):
    """Gets the natural log of a value."""
    
class log(MathFunction):
    """Gets the natural log of a value."""

class radians(MathFunction):
    """Degrees to radians of a value."""
    
class ROUND(MathFunction):
    """Gets the nearest integer to a value."""
    
class sign(MathFunction):
    """Gets the sign of the value."""
    
class sqrt(MathFunction):
    """Gets the square root of the value."""
    
class trunc(MathFunction):
    """Truncate the value."""

class acos(MathFunction):
    """Inverse cosine of the value."""
    
class asin(MathFunction):
    """Inverse sine of the value."""
    
class atan(MathFunction):
    """Inverse tangent of the value."""
    
class cos(MathFunction):
    """Cosine of the value."""
    
class cot(MathFunction):
    """Cotangent of the value."""
    
class sin(MathFunction):
    """Sine of the value."""
    
class tangent(MathFunction):
    """Tangent of the value."""
