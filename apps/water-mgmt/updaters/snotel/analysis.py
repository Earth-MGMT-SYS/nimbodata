
import sys, os
import datetime

sys.path.append('../../../../')

from client import pyclient

from common.datatypes import Text,Point,Date,Float
from common.expressions import extract,MIN,MAX,AVG,count,unique,Join

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('SnotelSites')
site_cols = dict((x['name'],x) for x in site_table.columns())
snam, ssnum = site_cols['site_name'], site_cols['site_no']

data_table = db.Table('SnotelData')
snum,obd,swe,pre,tma,tmi,tav,pri = data_table.columns()

try:
    db.View('Snow2013Data').drop()
except:
    pass
snowdata = db.create_view('Snow2013Data',{
    'objid':site_table,
    'where':[obd >= Date(2013,1,1),obd < Date(2014,1,1)],
    'join':Join(data_table),
},materialized=True)

try:
    db.View('Snow2013Sites').drop()
except:
    pass
siteid_view = db.create_view('Snow2013Sites',{
    'objid':snowdata,
    'cols':[unique(ssnum)]
},materialized=True)

try:
    db.View('Snow2013').drop()
except:
    pass
site_view = db.create_view('Snow2013',{
    'objid':site_table,
    'cols':['_adm-rowid']+site_table.columns(),
    'join':(siteid_view,('site_no','=','unique(site_no)'))
},materialized=True)

try:
    site_view.View('POR').drop()
except:
    pass
sitestart = site_view.create_view('POR',{
    'objid':site_table,
    'cols':['_adm-rowid',MIN(obd),MAX(obd),count(obd),site_cols['geom']],
    'join':Join(data_table),
    'group_by':['_adm-rowid',site_cols['geom']]
},materialized=True)

try:
    site_view.View('Peak2013').drop()
except:
    pass
peak2013 = site_view.create_view('Peak2013',{
    'objid':site_table,
    'cols':['_adm-rowid']+[snum,extract(obd,'year'),MAX(swe)],
    'where':[obd >= Date(2013,1,1),obd < Date(2014,1,1)],
    'join':Join(data_table),
    'group_by':['_adm-rowid']+[snum,extract(obd,'year')],
    'order_by':[snum,extract(obd,'year')]
},materialized=True)


try:
    site_view.View('PeakHistorical').drop()
    site_view.View('MaxHistorical').drop()
except:
    pass
maxhist = site_view.create_view('MaxHistorical',{
    'objid':site_table,
    'cols':['_adm-rowid']+[snum,MAX(swe)],
    'join':Join(data_table),
    'group_by':['_adm-rowid',snum],
    'order_by':[snum]
},materialized=True)

'''
site_view = db.View('Snow2013')
maxhist = site_view.View('MaxHistorical')
peak2013 = site_view.View('Peak2013')
'''

hcols = dict((x['name'],x) for x in maxhist.columns())
ycols = dict((x['name'],x) for x in peak2013.columns())

try:
    site_view.View('Data').drop()
except:
    pass
datatab = site_view.create_view('Data',{
    'objid':peakhist,
    'cols':['_adm-rowid']+[ycols['MAX(SnotelData.swe)'],
        hcols['MAX(SnotelData.swe)']
    ],
    'join':(peak2013,('site_no','=','site_no')) # Too many same name cols.
},materialized=True)

'''

try:
    db.View('SnotelSiteStart').drop()
except:
    pass
maxsnow = db.create_view('SnotelSiteStart',{
    'objid':site_table,
    'cols':['_adm-rowid',snam,ssnum,start,'geom'],
    'order_by':[start]
},materialized=True)

start = datetime.date(2013,10,01)

try:
    db.View('MaxAnnualSnow').drop()
except:
    pass
maxsnow = db.create_view('MaxAnnualSnow',{
    'objid':data_table,
    'cols':[snam,snum,extract(obd,'year'),MAX(swe)],
    'where':snum == 310,
    'join':(site_table,(snum,'=',ssnum)),
    'group_by':[snam,snum,extract(obd,'year')],
    'order_by':[snum,extract(obd,'year')]
})

try:
    db.View('DailySnow').drop()
except:
    pass
maxsnow = db.create_view('DailySnow',{
    'objid':data_table,
    'cols':[snam,snum,obd,swe],
    'where':((snum == 310) & (obd >= start)),
    'join':(site_table,(snum,'=',ssnum)),
    'order_by':[obd]
})

try:
    db.View('MinAnnualSnow').drop()
except:
    pass
maxsnow = db.create_view('MinAnnualSnow',{
    'objid':data_table,
    'cols':[snam,snum,extract(obd,'year'),MIN(swe)],
    'where':snum == 310,
    'join':(site_table,(snum,'=',ssnum)),
    'group_by':[snam,snum,extract(obd,'year')],
    'order_by':[snum,extract(obd,'year')]
})

try:
    db.View('AvgAnnualSnow').drop()
except:
    pass
maxsnow = db.create_view('AvgAnnualSnow',{
    'objid':data_table,
    'cols':[snam,snum,extract(obd,'year'),AVG(swe)],
    'where':snum == 310,
    'join':(site_table,(snum,'=',ssnum)),
    'group_by':[snam,snum,extract(obd,'year')],
    'order_by':[snum,extract(obd,'year')]
})


try:
    db.View('MaxDailySnow').drop()
except:
    pass
maxsnow = db.create_view('MaxDailySnow',{
    'objid':data_table,
    'cols':[snam,snum,extract(obd,'month'),extract(obd,'day'),MAX(swe)],
    'where':snum == 310,
    'join':(site_table,(snum,'=',ssnum)),
    'group_by':[snam,snum,extract(obd,'month'),extract(obd,'day')],
    'order_by':[snum,extract(obd,'month'),extract(obd,'day')]
})
'''
