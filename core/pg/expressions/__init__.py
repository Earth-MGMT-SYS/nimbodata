
import common.expressions as base

operators = base.operators

import prototype
import comparable
import math
import join
import time
import general

from prototype import *
from comparable import *
from math import *
from join import *
from time import *
from general import *

def inject_api(api):
    prototype.api = api
    comparable.api = api
    math.api = api
    join.api = api
    time.api = api
    general.api = api
