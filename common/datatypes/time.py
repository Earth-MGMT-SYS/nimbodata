"""Module implements date and time types."""
# Copyright (C) 2014  Bradley Alan Smith

import datetime

import dateutil.parser

from . import *

class Date(Datatype):
    
    def from_literal(self,*args,**kwargs):
        try:
            return dateutil.parser.parse(args[0]).date()
        except AttributeError:
            return datetime.date(*args,**kwargs)


class Timestamp(Datatype):
    
    def from_literal(self,*args,**kwargs):
        try:
            return dateutil.parser.parse(args[0])
        except AttributeError:
            return datetime.datetime(*args,**kwargs)
    

class Time(Datatype):
    
    def from_literal(self,*args,**kwargs):
        try:
            return dateutil.parser.parse(args[0]).time()
        except AttributeError:
            return datetime.time(*args,**kwargs)
