"""Module implements base numeric datatypes."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class BooleanArray(Datatype):
    
    from_literal = list

class IntegerArray(Datatype):
    
    from_literal = list

class FloatArray(Datatype):
    
    from_literal = list

class TextArray(Datatype):
    
    from_literal = list
