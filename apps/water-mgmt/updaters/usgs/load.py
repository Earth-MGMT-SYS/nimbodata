"""
Copyright (C) 2014  Bradley Alan Smith

"""

import datetime
import sys, os
from copy import copy

from itertools import repeat

sys.path.append('../../../../')
from apps.updater import *

# Take care of the file import
dataPath = './import-data'
infiles = [(f,os.path.join(dataPath,f))
    for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.csv']
try:
    db = cloud.Database('WaterMgmt')
    sites_u = Updater(UpdateFileDatabase('WaterMgmt',infiles,UpdateFileTable),db)
    sites_u.create()
except common.errors.RelationDoesNotExist:
    sites_u = Updater(UpdateFileDatabase('WaterMgmt',infiles,UpdateFileTable))
    db = sites_u.create()
sites_u.update()


# Now parameter codes, which are a single-URL table.
spec = [
    ('USGSParams',"http://nwis.waterdata.usgs.gov/usa/nwis/pmcodes?radio_pm_search=param_group&pm_group=All+--+include+all+parameter+groups&pm_search=&casrn_search=&srsname_search=&format=rdb&show=parameter_group_nm&show=parameter_nm&show=casrn&show=srsname&show=parameter_units"),
]

class SimpleUSGSTable(UpdateWebTable):
    """Encapsulate the unique character of a USGS table."""
   
    def process_result(self,text):
        header,rows = UpdateWebTable.process_result(self,text)
        if header is None and rows is None:
            return None, None
        return header, rows[1:] # First row after header is field lengths

param_u = Updater(UpdateWebDatabase('WaterMgmt',spec,SimpleUSGSTable), db)
param_u.create()
param_u.update()

# Now the sites.
spec = [('USGSSites',"http://waterservices.usgs.gov/nwis/site/?format=rdb&siteType=ST&stateCd=%(st)s&siteOutput=expanded&hasDataTypeCd=dv&parameterCd=00060" % {'st':st })
    for st in ('az','nm','tx','ca','co','or','wa','ut','wy','mt','id')]
site_u = Updater(UpdateWebDatabase('WaterMgmt',spec,SimpleUSGSTable),db)
site_u.create()
site_u.update()

class USGSParameterizedTable(UpdateWebTable):
    """Encapsulate the unique character of a USGS table."""
   
    def process_result(self,text):
        header,rows = UpdateWebTable.process_result(self,text)
        if header is None and rows is None:
            return None, None
        
        params = set()
        cols = []
        for col in header[3:]:
            cols.append(col)
            try:
                if col.rsplit('_',1)[1] == 'cd':
                    continue
            except IndexError as e:
                print header
                raise e
            params.add(col)
        
        new_header = [
            'agency_cd','site_no','datetime','dd','parametercode','statcode',
            'value','valuecode','valuetext'
        ]
        
        retVal = []
        for row in rows[1:]: # First row after header is field lengths
            stub = row[0:3]
            workrow = {
                'valuetext':None,
                'valuecode':None,
                'value':None
            }
            for col,val in zip(cols,row[3:]):
                if col.rsplit('_',1)[1] == 'cd':
                    workrow['valuecode'] = val
                    retVal.append(copy(stub) + [
                        workrow['dd'],
                        workrow['parametercode'],
                        workrow['statcode'],
                        workrow['value'],
                        workrow['valuecode'],
                        workrow['valuetext']
                    ])
                    workrow = {
                        'valuetext':None,
                        'valuecode':None,
                        'value':None
                    }
                else:
                    workrow['dd'],workrow['parametercode'],workrow['statcode']\
                            = col.split('_')
                    try:
                        workrow['value'] = float(val)
                    except ValueError:
                        workrow['valuetext'] = val
                    
        return new_header, retVal

sites = db.Table('USGSSites').select(['site_no'])


# Now the data itself
spec = []
for site in sites:
    url = "http://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=%(sitecode)s&startDT=2013-10-01&endDT=%(today)s"
    spec.append(('USGSData',url % {
        'sitecode':site[0],
        'today':datetime.date.today()
    }))
    
data_u = Updater(UpdateWebDatabase('WaterMgmt',spec,USGSParameterizedTable), db)
data_u.create()
data_u.update()



# Now the stats
spec = []
for site in sites:
    url = "http://waterservices.usgs.gov/nwis/stat/?format=rdb&sites=%(sitecode)s&statReportType=daily&statTypeCd=mean,min,max"
    spec.append(('USGSStats',url % {
        'sitecode':site[0]
    }))
data_u = Updater(UpdateWebDatabase('WaterMgmt',spec,SimpleUSGSTable), db)
data_u.create()
data_u.update()


print db.tables()
#table = db.Table('statscodes')
#print len(table.select())
table = db.Table('USGSSites')
print len(table.select())
#table = db.Table('USGS Data')
#print len(table.select())
    
