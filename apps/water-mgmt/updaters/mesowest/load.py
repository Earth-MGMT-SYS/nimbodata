"""
Copyright (C) 2014  Bradley Alan Smith

"""

import datetime
import sys, os
from copy import copy
import calendar
import datetime
from bs4 import BeautifulSoup

from itertools import repeat

sys.path.append('../../../../')
from apps.updater import *


db = cloud.Database('WaterMgmt')



class mesowestsites(UpdateWebTable):
    
    header = ['StationID','StationName','State','Lat','Lon','Elev','ElevUnits','Mnet']
    cuts = [5,41,46,57,70,76,81]
    
    def process_result(self,text):
        soup = BeautifulSoup(text)
        text = soup.get_text()
        collect = False
        rows = []
        for row in text.split('\n'):
            if collect is False and row.startswith('--'):
                collect = True
                continue
            elif collect:
                newrow = []
                last = 0
                for c in self.cuts:
                    newrow.append(row[last:c].strip())
                    last = c
                newrow.append(row[81:])
                rows.append(newrow)
        return self.header,rows

try:
    db.Table('MesowestSites').drop()
except common.errors.RelationDoesNotExist:
    pass

site_spec = [
    ('MesowestSites','http://mesowest.utah.edu/cgi-bin/droman/meso_station.cgi?area=1')
]

updb = UpdateWebDatabase('WaterMgmt',site_spec,mesowestsites)
mesow_u = Updater(updb, db)
mesow_u.create()
mesow_u.update()


