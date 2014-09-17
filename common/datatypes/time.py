"""Module implements date and time types."""
# Copyright (C) 2014  Bradley Alan Smith

import datetime

import jsonpickle

from . import *

class Date(Datatype):
    
    def from_literal(self,*args,**kwargs):
        try:
            return jsonpickle.decode(args[0])
        except TypeError:
            return datetime.date(*args,**kwargs)


class Timestamp(Datatype):
    
    def from_literal(self,*args,**kwargs):
        try:
            return jsonpickle.decode(args[0])
        except TypeError:
            return datetime.datetime(*args,**kwargs)
    

class Time(Datatype):
    
    def from_literal(self,*args,**kwargs):
        try:
            return jsonpickle.decode(args[0])
        except TypeError:
            return datetime.time(*args,**kwargs)
