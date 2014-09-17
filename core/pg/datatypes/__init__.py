"""Module implements PostgreSQL datatypes for Nimbodata.

Implements datatypes for the platform - handles serialization and
database interaction (encapsulates SQL for creating, formatting and aliasing
the datatypes).

"""
# Copyright (C) 2014  Bradley Alan Smith

import inspect

from common.datatypes.prototype import Datatype
from pg_prototype import PG_Datatype

import common.datatypes.geographic

from geographic import *
from numeric import *
from text import *
from time import *
from function import *
from ranges import *
from dataobject import *

# Supports the idiom where the object represents the Type and can be called
# to instantiate a value
Text = Text()
Integer = Integer()
Float = Float()
Point = Point()
MultiPoint = MultiPoint()
Line = Line()
MultiLine = MultiLine()
Polygon = Polygon()
MultiPolygon = MultiPolygon()
Boolean = Boolean()
Json = Json()
Date = Date()
Timestamp = Timestamp()
Time = Time()
IntegerRange = IntegerRange()
DataObject = DataObject()

import _register_lunatics

