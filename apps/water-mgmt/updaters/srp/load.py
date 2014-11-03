"""
Copyright (C) 2014  Bradley Alan Smith

"""
from itertools import product

import datetime
import sys, os
from copy import copy
import calendar
import datetime
from bs4 import BeautifulSoup

from itertools import repeat

sys.path.append('../../../../')
from apps.updater import *



# Take care of the file import
dataPath = './import-data'
infiles = [(f,os.path.join(dataPath,f))
    for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.csv']
try:
    db = cloud.Database('WaterMgmt')
    try:
        db.Table('SRPReservoirs').drop()
    except common.errors.RelationDoesNotExist:
        pass
    sites_u = Updater(UpdateFileDatabase('WaterMgmt',infiles,UpdateFileTable),db)
    sites_u.create()
except common.errors.RelationDoesNotExist:
    sites_u = Updater(UpdateFileDatabase('WaterMgmt',infiles,UpdateFileTable))
    db = sites_u.create()
sites_u.update()

db = cloud.Database('WaterMgmt')
sites = db.Table('SRPReservoirs')

try:
    db.Table('SRPResData').drop()
except common.errors.RelationDoesNotExist:
    pass
    
months = {v.lower(): k for k,v in enumerate(calendar.month_name)}

spec = []
for mo,day,yr in product(range(1,13), range(1,32), range(2008,2015)):
    repl = {'mo':mo,'dy':day,'yr':yr}
    spec.append(
        (
            'SRPResData',
            'https://www.srpwater.com/dwr/report.aspx?dt=%(yr)s/%(mo)s/%(dy)s' % repl
        )
    )

class srpdata(UpdateWebTable):
    """Encapsulate the unique character of the SRP water report."""
   
    header = ['StationID','date','elev','content']
    
    def process_result(self,text):
        
        soup = BeautifulSoup(text)
        trs = soup.find('table').find_all_next('tr')
        sitenames = ('Roosevelt','Horse Mesa', 'Mormon Flat', 'Stewart Mtn', 
            'Horseshoe', 'Bartlett')
        outrows = []
        date = None
        done = []
        
        for row in trs:
            rowheaders = [x for x in row.find_all_next('th')]
            if date is None and len(rowheaders) > 0 \
                    and rowheaders[0].text.startswith('For '):
                date = rowheaders[0].text.replace(',','').split()
                month = str(months[date[2].lower()])
                day = str(int(date[3]))
                year = int(date[4])
                day = day if len(day) > 1 else '0' + day
                month = month if len(month) > 1 else '0' + month
                date = '%s-%s-%s' % (year,month,day)
            rowcells = [x for x in row.find_all_next('td')]
            if rowcells[0].text in sitenames and rowcells[0].text not in done:
                done.append(rowcells[0].text)
                newrow = [
                    rowcells[0].text.replace(' ',''),
                    date,
                    rowcells[1].text.replace('"','').replace(',',''),
                    rowcells[4].text.replace('"','').replace(',','')
                ]
                outrows.append(newrow)
        
        return self.header,outrows

updb = UpdateWebDatabase('WaterMgmt',spec,srpdata)
srp_u = Updater(updb, db)

srp_u.create()
srp_u.update()
