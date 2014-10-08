"""Module implements the comparable base class and BinaryExpression."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class Comparable(base.Comparable):
    """Override comparison operators for relational use."""
    
    def sql(self):
        return "dickbutt"
        
    
