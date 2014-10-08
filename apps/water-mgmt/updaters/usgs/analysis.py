
import sys, os
from pprint import pprint

sys.path.append('../../../../')
from client import pyclient
from core.pg.datatypes import Text,Point,Date,Float
from common.expressions import extract,MIN,MAX,AVG,count,unique,Join
user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('USGSSites')
site_cols = dict((x['name'],x) for x in site_table.columns())
site_no, station_nm = site_cols['site_no'], site_cols['station_nm']

data_table = db.Table('USGSData')
data_cols = dict((x['name'],x) for x in data_table.columns())
d_site_no,pcode,scode = data_cols['site_no'],data_cols['parametercode'],data_cols['statcode']
dt,value,valuecode = data_cols['datetime'],data_cols['value'],data_cols['valuecode']

#'''

try:
    db.View('Streams2013Data').drop()
except:
    pass
streamsdata = db.create_view('Streams2013Data',{
    'objid':site_table,
    'where':[dt >= Date(2013,1,1),data_cols['parametercode'] == '00060',
        data_cols['statcode'] == '00003',dt < Date(2014,1,1)
    ],
    'join':(data_table,(site_no,'=',d_site_no)),
},materialized=True)

try:
    db.View('Streams2013Sites').drop()
except:
    pass
siteid_view = db.create_view('Streams2013Sites',{
    'objid':streamsdata,
    'cols':[unique(site_no)]
},materialized=True)


try:
    db.View('Streams2013').drop()
except:
    pass
site_view = db.create_view('Streams2013',{
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
    'cols':['_adm-rowid',MIN(dt),MAX(dt),count(dt),site_cols['geom']],
    'where':((pcode == '00060') & (scode == '00003')),
    'join':(data_table,(site_no,'=',d_site_no)),
    'group_by':[
        '_adm-rowid','huc_cd','drain_area_va',site_cols['geom']
    ]
},materialized=True)


data_cols = dict((x['name'],x) for x in data_table.columns())

try:
    site_view.View('Peak2013').drop()
except:
    pass
peak2013 = site_view.create_view('Peak2013',{
    'objid':site_table,
    'cols':['_adm-rowid']+[data_cols['site_no'],extract(data_cols['datetime'],'year'),
        MAX(data_cols['value']),data_cols['valuecode']
    ],
    'where':[dt >= Date(2013,1,1),data_cols['parametercode'] == '00060',
        data_cols['statcode'] == '00003',dt < Date(2014,1,1)
    ],
    'join':(data_table,('site_no','=','site_no')),
    'group_by':['_adm-rowid','station_nm']+[data_cols['site_no'],
        extract(data_cols['datetime'],'year'),
        data_cols['valuecode']
    ],
    'order_by':[d_site_no,extract(data_cols['datetime'],'year')]
},materialized=True)


stats = db.Table('USGSStats')
stat_cols = dict((x['name'],x) for x in stats.columns())

try:
    site_table.View('StreamsMonthlyStats').drop()
    site_view.View('StreamsMonthlyStats').drop()
except:
    pass    
site_view.create_view('StreamsMonthlyStats',{
    'objid':stats,
    'cols':[stat_cols['site_no'],stat_cols['month_nu'],MAX(stat_cols['max_va']),
        AVG(stat_cols['mean_va']),MIN(stat_cols['min_va'])],
    'group_by':[stat_cols['site_no'],stat_cols['month_nu']],
    'order_by':[stat_cols['site_no'],stat_cols['month_nu']]
},materialized=True)

try:
    site_view.View('PeakHistorical').drop()
    site_view.View('MaxHistorical').drop()
except:
    pass
maxhist = site_view.create_view('MaxHistorical',{
    'objid':site_table,
    'cols':['_adm-rowid']+[stat_cols['site_no'],MAX(stat_cols['max_va'])],
    'where':[stat_cols['parameter_cd'] == '00060'],
    'join':(stats,('site_no','=','site_no')),
    'group_by':['_adm-rowid']+[stat_cols['site_no']],
    'order_by':[stat_cols['site_no']]
},materialized=True)

'''
site_view = db.View('Streams2013')
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
    'objid':maxhist,
    'cols':['_adm-rowid']+[ycols['MAX(USGSData.value)'],
        hcols['MAX(USGSStats.max_va)']
    ],
    'join':Join(peak2013,hcols['site_no'] == ycols['site_no'])
},materialized=True)




