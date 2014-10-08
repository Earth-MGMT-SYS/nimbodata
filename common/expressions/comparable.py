"""Module implements the comparable base class and BinaryExpression."""
# Copyright (C) 2014  Bradley Alan Smith

from .. import errors
from prototype import *
from . import *

# The operator list may be appended to by other modules implementing extended
# operators.  Needs to be incorporated into CloudAPI.        


class Comparable(object):
    """Override comparison operators for relational use."""
    
    def __lt__(self,other):
        return BinaryExpression(self,'<',other)
        
    def __gt__(self,other):
        return BinaryExpression(self,'>',other)
        
    def __eq__(self,other):
        return BinaryExpression(self,'=',other)
        
    def __ne__(self,other):
        return BinaryExpression(self,'<>',other)
        
    def __le__(self,other):
        return BinaryExpression(self,'<=',other)
        
    def __ge__(self,other):
        return BinaryExpression(self,'>=',other)

    def __add__(self,other):
        return BinaryExpression(self,'+',other)
    
    def __sub__(self,other):
        return BinaryExpression(self,'-',other)
        
    def __mul__(self,other):
        return BinaryExpression(self,'*',other)
        
    def __div__(self,other):
        return BinaryExpression(self,'/',other)
        
    def __pow__(self,other):
        return BinaryExpression(self,'^',other)
    
