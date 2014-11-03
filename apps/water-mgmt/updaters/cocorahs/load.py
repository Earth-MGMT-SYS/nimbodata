"""
Copyright (C) 2014  Bradley Alan Smith

"""

import datetime
import sys, os
from copy import copy

from itertools import repeat

sys.path.append('../../../../')
from apps.updater import *
from common.expressions import unique

db = cloud.Database('WaterMgmt')
try:
    db.Table('CoCoRaHSAnnuals').drop()
except common.errors.RelationDoesNotExist:
    pass

# Now the sites.
spec = [('CoCoRaHSAnnuals',"http://www.cocorahs.org/WaterYearSummary/2013-2014/%(st)s-wys-2014.xls" % {'st':st })
    for st in ('az','nm','tx','ca','co','or','wa','ut','wy','mt','id','nv','can')]
site_u = Updater(UpdateWebDatabase('WaterMgmt',spec,UpdateWebXLTable),db)
site_u.create()
site_u.update()

siteid = db.Table('CoCoRaHSAnnuals').columns()[0]
