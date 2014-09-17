"""Module implements base numeric datatypes."""
# Copyright (C) 2014  Bradley Alan Smith

from . import *

class Boolean(Datatype):
    
    from_literal = bool

class Integer(Datatype):
    
    from_literal = int

class Float(Datatype):
    
    from_literal = float
