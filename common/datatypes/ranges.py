"""Module implements range datatypes in Nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class NumericRange(object):
    
    def from_literal(self,*args,**kwargs):
        return type(self)(*args,**kwargs)
    
    def __init__(self,value=None,cur=None,conv = None):
        self.value = value
        if value is not None:
            self.bounds = value[0]+value[-1]
            ends = value[1:-1].split(',')
            self.lower, self.upper = [int(x) for x in ends]
        
    def __str__(self):
        return self.value
    
    def __contains__(self,value):
        if self.bounds == '()':
            if self.lower < value < self.upper:
                return True
            else:
                return False
        elif self.bounds == '[]':
            if self.lower <= value <= self.upper:
                return True
            else:
                return False
        elif self.bounds == '[)':
            if self.lower <= value < self.upper:
                return True
            else:
                return False
        elif self.bounds == '(]':
            if self.lower < value < self.upper:
                return True
            else:
                return False
    
    def toJSON(self):
        return self.value


class IntegerRange(NumericRange,Datatype):
    
    def __init__(self,value=None,cur=None):
        if value is not None:
            NumericRange.__init__(self,value,conv = int)
    

class LongRange(NumericRange,Datatype):

    def __init__(self,value=None,cur=None):
        if value is not None:
            NumericRange.__init__(self,value,conv = long)


class FloatRange(NumericRange,Datatype):
    
    def __init__(self,value=None,cur=None):
        if value is not None:
            NumericRange.__init__(self,value,conv = float)
