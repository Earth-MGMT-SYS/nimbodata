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


db = cloud.Database('WaterMgmt')
sites = db.Table('CDECReservoirs')

try:
    db.Table('CDECResData').drop()
except common.errors.RelationDoesNotExist:
    pass
    
months = {v.lower(): k for k,v in enumerate(calendar.month_name)}

content_spec = []
info_spec = []
for siteinfo in sites.select():
    repl = siteinfo['StationID']
    content_spec.append(
        (
            'CDECResData',
            "http://cdec.water.ca.gov/cgi-progs/queryCSV?station_id=%s&sensor_num=15&dur_code=D&start_date=2013-01-01&end_date=&data_wish=View+CSV+Data" % repl
        )
    )
    
    info_spec.append(
        (
            'CDECResInfo',
            'http://cdec.water.ca.gov/cgi-progs/profile?s=%s&type=res' % repl
        )
    )

class cdecresinfo(UpdateWebTable):
    
    header = ['StationID','Capacity']
    
    def process_result(self,text):
        soup = BeautifulSoup(text)
        siteid = soup.find('h1')
        siteid = siteid.find_next('i').get_text()[2:-1]
        print siteid
        t = soup.find('table')
        try:
            tds = (x for x in t.find_all_next('td'))
        except AttributeError:
            print siteid + " SKIPPING BECUASE ERROR!"
            return None, None
        for td in tds:
            if td.get_text() == 'Capacity':
                cap = next(tds).get_text()[:-3].replace(',','')
                return self.header,[(siteid,cap)]

class cdecdata(UpdateWebTable):
    """Encapsulate the unique character of the BOR elevations web table."""
   
    header = ['StationID','date','content']
    
    def process_result(self,text):
        outrows = []
        rows = text.split('\n')
        try:
            siteid = rows[0].split(': "')[1].split('.')[0]
        except IndexError:
            return None,None
        
        for row in rows[2:]:
            spl = row.split(',')
            if len(spl) != 3:
                continue
            try:
                dt = '%(yr)s-%(mo)s-%(dy)s' % {
                    'yr':spl[0][0:4],
                    'mo':spl[0][4:6],
                    'dy':spl[0][6:]
                }
                outrows.append((siteid,dt,spl[2][0:-1])) # carriage return, blech
            except IndexError:
                print spl
        return self.header,outrows

updb = UpdateWebDatabase('WaterMgmt',info_spec,cdecresinfo)
bor_u = Updater(updb, db)

bor_u.create()
bor_u.update()

updb = UpdateWebDatabase('WaterMgmt',content_spec,cdecdata)
bor_u = Updater(updb, db)

bor_u.create()
bor_u.update()

