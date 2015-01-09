"""Module implements PostgreSQL entities as Python objects for Nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith

import inspect
import sys
import json

import psycopg2

try:
    from common import results
    import common.errors as errors
except ImportError:
    from nimbodata.common import results
    import nimbodata.common.errors as errors


from .. import engine
from .. import select


controllers = {
    'dml':engine.Engine(),
    'ddl':engine.Engine(),
    'drc':engine.Engine(),
    'dql':select.Select()
}

bases = []
api = None # Injected by the create API function

from prototype import *
# We have to make the controller objects available to the individual modules
prototype.controllers = controllers

from database import *
database.controllers = controllers

from view import *
view.controllers = controllers

from table import *
table.controllers = controllers

from column import *
column.controllers = controllers

from constraint import *
constraint.controllers = controllers

for mod in (prototype,column,constraint,database,view,table):
    for cls in inspect.getmembers(mod,inspect.isclass):
        if isinstance(cls[1](),Entity):
            bases.append(cls[1])
