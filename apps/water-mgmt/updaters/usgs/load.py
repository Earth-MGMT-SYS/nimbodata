"""
Copyright (C) 2014  Bradley Alan Smith

"""

import datetime
import sys, os

from itertools import repeat

sys.path.append('../../')
from apps.updater import *

dataPath = './import-data'

infiles = [(f,os.path.join(dataPath,f))
    for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.csv']

sites_u = Updater(UpdateFileDatabase('USGS',infiles,UpdateFileTable))
db = sites_u.create()
sites_u.update()

spec = [
    ('USGS Parameters',"http://nwis.waterdata.usgs.gov/usa/nwis/pmcodes?radio_pm_search=param_group&pm_group=All+--+include+all+parameter+groups&pm_search=&casrn_search=&srsname_search=&format=rdb&show=parameter_group_nm&show=parameter_nm&show=casrn&show=srsname&show=parameter_units"),
]

class USGSTable(UpdateWebTable):
   
   def process_result(self,text):
       header,rows = UpdateWebTable.process_result(self,text)
       if header is None and rows is None:
           return None, None
       return header, rows[1:]

param_u = Updater(UpdateWebDatabase('USGS',spec,USGSTable), db)

param_u.create()
param_u.update()

spec = [('USGS Sites',"http://waterservices.usgs.gov/nwis/site/?format=rdb&siteType=ST&stateCd=%(st)s&siteOutput=expanded&hasDataTypeCd=dv&parameterCd=00060" % {'st':st })
    for st in ('az','nm')]#,'tx','ca','or','wa','ut','wy','mt','id')]

site_u = Updater(UpdateWebDatabase('USGS',spec,USGSTable), db)
site_u.create()
site_u.update()

sites = db.Table('USGS Sites').select(['site_no'])

spec = []
for site in sites:
    url = "http://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=%(sitecode)s&startDT=2013-10-01&endDT=%(today)s"
    spec.append(('USGS Data',url % {
        'sitecode':site[0],
        'today':datetime.date.today()
    }))
    
data_u = Updater(UpdateWebDatabase('USGS',spec,USGSTable), db)
data_u.create()
data_u.update()

spec = []
for site in sites:
    url = "http://waterservices.usgs.gov/nwis/stat/?format=rdb&sites=%(sitecode)s&statReportType=daily&statTypeCd=all"
    spec.append(('USGS Stats',url % {
        'sitecode':site[0]
    }))
    
data_u = Updater(UpdateWebDatabase('USGS',spec,USGSTable), db)
data_u.create()
data_u.update()

print db.tables()
table = db.Table('statscodes')
print len(table.select())
table = db.Table('USGS Sites')
print len(table.select())
table = db.Table('USGS Data')
print len(table.select())
    
