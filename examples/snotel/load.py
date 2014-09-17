"""
Copyright (C) 2014  Bradley Alan Smith

"""

import sys, os

from itertools import repeat

sys.path.append('../../')
from apps.updater import *

dataPath = './import-data'

infiles = [(f,os.path.join(dataPath,f))
    for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.csv']

sites_u = Updater(UpdateFileDatabase('Snotel',infiles,UpdateFileTable))
db = sites_u.create()
sites_u.update()

sites = db.Table('sites').select(['site_name','state'])

url_templ = """http://www.wcc.nrcs.usda.gov/reportGenerator/view_csv/customSingleStationReport/daily/{site number}:{state}:SNTL%7Cid=%22%22%7Cname/POR_BEGIN,POR_END/WTEQ::value,PREC::value,TMAX::value,TMIN::value,TAVG::value,PRCP::value"""
def fmt_url(site):
    site_no = site[0].split('(')[1].replace(')','')
    return url_templ.format(**{'site number':site_no,'state':site[1]})

urls = (fmt_url(site) for site in sites)

spec = zip(repeat('Values'),urls)[0:3]

values_u = Updater(UpdateWebDatabase('Snotel',spec,UpdateWebTable), db)

values_u.create()
print db.tables()
values_u.tables = repeat(db.Table('Values'))

values_u.update()

for fname,fpath in infiles:
    print db.tables()
    table = db.Table('sites')
    print len(table.select())
    table = db.Table('Values')
    print len(table.select())
    
