
from . import *

class TimeFunction(Function):
    """Base class for any math MathFunction in PostgreSQL."""


# CONSTANTS/OTHER
   

# VALUE
class extract(TimeFunction):
    """Gets a component of a date, time or timestamp."""
    
    fields = [
        'century','day','decade','dow','doy','epoch','hour','isodow','isoyear',
        'microseconds','millenium','milliseconds','minute','month','quarter',
        'second','timezone','timezone_hour','timezone_minute','week','year',
        'water_year'
    ]
    
    def __int__(self,target,field):
        self.target,self.field = target,field

class now(TimeFunction):
    """Just like it sounds"""
