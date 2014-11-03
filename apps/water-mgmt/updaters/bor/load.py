"""
Copyright (C) 2014  Bradley Alan Smith

"""

import datetime
import sys, os
from copy import copy
import calendar
import datetime

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


try:
    db.Table('LCResData').drop()
except common.errors.RelationDoesNotExist:
    pass
    
try:
    db.Table('LCResMonthly').drop()
except common.errors.RelationDoesNotExist:
    pass
    
months = {v.lower(): k for k,v in enumerate(calendar.month_name)}

spec = []
for yr in range(2000,2015):
    for mo in range(1,13):
        mo = str(mo)
        mo = mo if len(mo) > 1 else '0'+mo
        repl = {'year':yr,'month':mo}
        spec.append(
            (
                'LCResData',
                "http://www.usbr.gov/lc/region/g4000/archives_report.cfm?DIR=cy%(year)s&FILE=%(month)s_%(year)s" % repl
            )
        )

class borelevations(UpdateWebTable):
    """Encapsulate the unique character of the BOR elevations web table."""
   
    header = ['date','site_name','elev','content','release']
   
    def process_result(self,text):
        cont = True
        text = (x for x in text.split('\n'))
        
        while cont:
            row = next(text)
            if row.startswith('                                                     AVAILABLE RESERVOIR ELEVATIONS AND CONTENTS FOR '):
                monthname,year = row.split()[-2:]
                continue
            elif row.startswith('     DAY  STORAGE**   SPACE'):
                assert next(text).startswith('--')
                break
        
        monthrows = []
        for i in xrange(31):
            row = next(text)
            row = row.split()
            if len(row) != 16:
                break
            obd = '%(year)s-%(month)s-%(day)s' % {
                'year':year,
                'month':months[monthname.lower()],
                'day':row[0]
            }
            monthrows.append([obd,'Mead',row[3],row[4],row[5]])
            monthrows.append([obd,'Mohave',row[6],row[7],row[8]])
            monthrows.append([obd,'Havasu',row[9],row[10],row[11]])
            monthrows.append([obd,'SenatorWash',row[9],row[10],row[12]])
        
        while cont:
            row = next(text)
            if '-' in row:
                break
        
        
        
        for i in xrange(31):
            row = next(text)
            row = row.split()
            if len(row) != 17:
                break
            obd = '%(year)s-%(month)s-%(day)s' % {
                'year':year,
                'month':months[monthname.lower()],
                'day':row[0]
            }
            monthrows.append([obd,'Powell',row[2],row[3],row[4]])
            monthrows.append([obd,'FlamingGorge',row[5],row[6],row[7]])
            monthrows.append([obd,'Navajo',row[8],row[9],row[10]])
            monthrows.append([obd,'BlueMesa',row[11],row[12],row[13]])
            monthrows.append([obd,'MorrowPoint',row[14],row[15],row[16]])
            
        return self.header,monthrows

class bormonthly(UpdateWebTable):
    """Gosh these are fun"""
    
    header = ['siteid','year','month','value']
    
    def process_result(self,text):
        cont = True
        text = (x for x in text.split('\n'))
        
        while cont:
            row = next(text)
            if '<H2><B>LAKE MEAD AT HOOVER DAM, ELEVATION (FEET)</B></H2>' in row:
                site = 'Mead'
            elif '<H2><B>LAKE MOHAVE AT DAVIS DAM, ELEVATION (FEET)</B></H2>' in row:
                site = 'Mohave'
            elif '<H2><B>LAKE HAVASU NEAR PARKER DAM, ELEVATION (FEET)</B></H2>' in row:
                site = 'Havasu'
            
            if row.startswith('Year'):
                break
        
        outrows = []
        for x in text:
            if x.startswith('**'):
                break
            row = x.split()
            for i in range(1,13):
                try:
                    outrows.append([site,int(row[0]),i,float(row[i])])
                except ValueError:
                    outrows.append([site,int(row[0]),i,None])
                except IndexError:
                    break
        
        return self.header,outrows

updb = UpdateWebDatabase('WaterMgmt',spec,borelevations)
bor_u = Updater(updb, db)

bor_u.create()
bor_u.update()

spec = [
    ['LCResMonthly','http://www.usbr.gov/lc/region/g4000/hourly/mead-elv.html'],
    ['LCResMonthly','http://www.usbr.gov/lc/region/g4000/hourly/moh-elv.html'],
    ['LCResMonthly','http://www.usbr.gov/lc/region/g4000/hourly/hav-elv.html'],
]

updb = UpdateWebDatabase('WaterMgmt',spec,bormonthly)
bor_u = Updater(updb, db)

bor_u.create()
bor_u.update()


