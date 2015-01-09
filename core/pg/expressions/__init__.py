
try:
    import common.expressions as base
except ImportError:
    import nimbodata.common.expressions as base

_expressions_modules = []
def getexp(name):
    for mod in _expressions_modules:
        try:
            attr = getattr(mod,name)
            return attr
        except AttributeError:
            continue

operators = base.operators

import prototype
import comparable
import math
import join
import time
import general
import geo
import where

from prototype import *
from comparable import *
from math import *
from join import *
from time import *
from general import *
from geo import *
from where import *

def inject_api(api):
    prototype.api = api
    comparable.api = api
    math.api = api
    join.api = api
    time.api = api
    general.api = api
    geo.api = api

_expressions_modules += [prototype,comparable,math,join,time,general,geo,where]
