"""Process stream flow data and aggregate by HUC region."""

import sys, os
from pprint import pprint

sys.path.append('../../../../')
from client import pyclient
from core.pg.datatypes import Text,Point,Date,Float
from common.expressions import extract,MIN,MAX,AVG,SUM,count,unique,Join,simplify
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

def indexall(rel):
    for col in rel.columns():
        rel.add_index(col)
    try:
        rel.add_index('_adm-rowid')
    except ValueError:
        pass


try:
    db.View('Streams2014Data').drop()
except:
    pass
streamsdata = db.create_view('Streams2014Data',{
    'objid':site_table,
    'where':[dt >= Date(2013,10,1),data_cols['parametercode'] == '00060',
        data_cols['statcode'] == '00003',dt < Date(2014,10,1)
    ],
    'join':(data_table,(site_no,'=',d_site_no)),
},materialized=True)

try:
    db.View('Streams2014Sites').drop()
except:
    pass
siteid_view = db.create_view('Streams2014Sites',{
    'objid':streamsdata,
    'cols':[unique(site_no)]
},materialized=True)

indexall(siteid_view)

try:
    db.View('Streams2014').drop()
except:
    pass
site_view = db.create_view('Streams2014',{
    'objid':site_table,
    'cols':['_adm-rowid']+site_table.columns(),
    'join':(siteid_view,('site_no','=','unique(site_no)'))
},materialized=True)

indexall(site_view)


stats = db.Table('USGSStats')
stat_cols = dict((x['name'],x) for x in stats.columns())

try:
    db.View('StreamPOR').drop()
except:
    pass
sitestart = db.create_view('StreamPOR',{
    'objid':site_table,
    'cols':['_adm-rowid',MIN(stat_cols['begin_yr']),MAX(stat_cols['end_yr']),
        SUM(stat_cols['count_nu']),site_cols['geom']
    ],
    'where':stat_cols['parameter_cd'] == '00060',
    'join':(stats,('site_no','=','site_no')),
    'group_by':[
        '_adm-rowid',site_cols['geom']
    ]
},materialized=True)

indexall(sitestart)

data_cols = dict((x['name'],x) for x in data_table.columns())

try:
    db.View('StreamPeak2014').drop()
except:
    pass
peak2014 = db.create_view('StreamPeak2014',{
    'objid':site_table,
    'cols':['_adm-rowid']+[data_cols['site_no'],AVG(data_cols['value'])],
    'where':[dt >= Date(2013,10,1),data_cols['parametercode'] == '00060',
        data_cols['statcode'] == '00003',dt < Date(2014,10,1)
    ],
    'join':(data_table,('site_no','=','site_no')),
    'group_by':['_adm-rowid','station_nm']+[data_cols['site_no']
    ],
    'order_by':[d_site_no]
},materialized=True)

indexall(peak2014)

stats = db.Table('USGSStats')
stat_cols = dict((x['name'],x) for x in stats.columns())

try:
    db.View('StreamMonthlyStats').drop()
except:
    pass    
mostat = db.create_view('StreamMonthlyStats',{
    'objid':stats,
    'cols':[stat_cols['site_no'],stat_cols['month_nu'],MAX(stat_cols['max_va']),
        AVG(stat_cols['mean_va']),MIN(stat_cols['min_va'])],
    'group_by':[stat_cols['site_no'],stat_cols['month_nu']],
    'order_by':[stat_cols['site_no'],stat_cols['month_nu']]
},materialized=True)

indexall(mostat)

try:
    db.View('StreamMaxHistorical').drop()
except:
    pass
maxhist = db.create_view('StreamMaxHistorical',{
    'objid':site_table,
    'cols':['_adm-rowid']+[stat_cols['site_no'],AVG(stat_cols['mean_va'])],
    'where':[stat_cols['parameter_cd'] == '00060'],
    'join':(stats,('site_no','=','site_no')),
    'group_by':['_adm-rowid']+[stat_cols['site_no']],
    'order_by':[stat_cols['site_no']]
},materialized=True)

indexall(maxhist)

hcols = dict((x['name'],x) for x in maxhist.columns())
ycols = dict((x['name'],x) for x in peak2014.columns())


try:
    db.View('StreamData').drop()
except:
    pass
datatab = db.create_view('StreamData',{
    'objid':maxhist,
    'cols':['_adm-rowid']+[ycols['AVG(USGSData.value)'],
        hcols['AVG(USGSStats.mean_va)']
    ],
    'join':Join(peak2014,hcols['site_no'] == ycols['site_no'])
},materialized=True)

indexall(datatab)

avy,avh = datatab.columns()

try:
    db.View('Stream').drop()
except:
    pass
site_view = db.create_view('Stream',{
    'objid':datatab,
    'where':avh > 0,
    'cols':['_adm-rowid'] + site_view.columns()[:-1] + [avy / avh, 'geom'],
    'join':Join(site_view,('_adm-rowid','=','_adm-rowid'))
},materialized=True)

indexall(site_view)

site_view = db.View('Stream')
stats = db.Table('USGSStats')
stat_cols = dict((x['name'],x) for x in stats.columns())
strvw = db.View('Stream')
scols = dict((x['name'],x) for x in site_view.columns())
acol = site_view.columns()[-2]

raw = db.View('Streams2014Data')
rcols = dict((x['name'],x) for x in raw.columns())
rdt,rval = rcols['datetime'],rcols['value']

for hlev in ('2','4','6'):
    base = db.Table('HUC'+hlev)
    cols = base.columns()
    hucols = dict((x['name'],x) for x in cols)
    try:
        site_view.View('HUC'+hlev).drop()
    except:
        pass
    zvw = site_view.create_view('HUC'+hlev,{
        'objid':base,
        'cols':['_adm-rowid']+[AVG(acol)]+[cols[-1]],
        'join':(site_view,(cols[-1].contains(scols['geom']))),
        'group_by':['_adm-rowid',cols[-1]]
    },materialized=True)
    
    zvw.columns()[-1].modify({'name':'geom','alias':'geom'})
    zvw.columns()[-2].modify({'name':'magnitude','alias':'Proportion of Historical Average'})
    indexall(zvw)
    
    dt = rcols['datetime']
    
    try:
        site_view.View('CurrentDaily_HUC'+hlev).drop()
    except:
        pass
    dhuc = site_view.create_view('CurrentDaily_HUC'+hlev,{
        'objid':base,
        'cols':['_adm-rowid']+[
            rdt,SUM(rval),SUM(stat_cols['min_va']),
            SUM(stat_cols['mean_va']),SUM(stat_cols['max_va'])
        ],
        'join':[
            (raw,(cols[-1].contains(rcols['geom']))),
            (stats,
                {'all':[
                    (rcols['site_no'] == stat_cols['site_no']),
                    (extract(dt,'month') == stat_cols['month_nu']),
                    (extract(dt,'day') == stat_cols['day_nu']),
                ]}
            )
        ],
        'group_by':['_adm-rowid',rdt],
        'order_by':['_adm-rowid',rdt],
    },materialized=True)
    
    indexall(dhuc)


site_view = db.View('Stream')
datatab = db.View('StreamData')
peak2014 = site_view.View('StreamPeak2014')
streamsdata = db.View('Streams2014Data')

h1, h2, h3 = site_view.View('HUC2'), site_view.View('HUC4'), site_view.View('HUC6')
h4 = h5 = h3
dpts = site_view
sch = {}
for z in range(19):
    base = None
    if z in range(0,5):
        base = h1
        hlev = site_view.View('CurrentDaily_HUC2')
    elif z < 6:
        base = h2
        hlev = site_view.View('CurrentDaily_HUC4')
    elif z < 7:
        base = h3
        hlev = site_view.View('CurrentDaily_HUC6')
    
    if base is not None:
        cols = base.columns()
        try:
            db.View('HUCz'+str(z)).drop()
        except:
            pass
        zvw = db.create_view('HUCz'+str(z),{
            'objid':base,
            'cols':['_adm-rowid']+cols[:-1]+[simplify('geom',5/(3**float(z)))]
        },materialized=True)
        zvw.columns()[-1].modify({'name':'geom','alias':'geom'})
        indexall(zvw)
        dvw = zvw.create_view('CurrentDaily',{'objid':hlev})
    else:
        zvw = site_view
    
    sch[z] = zvw
    

site_view.modify({'dobj':{'tilescheme':sch}})

site_view.columns()[-2].modify({'name':'magnitude','alias':'Proportion of Historical Average'})

dcols = dict((x['name'],x) for x in streamsdata.columns())
scols = dict((x['name'],x) for x in site_view.columns())

try:
    site_view.View('Stats').drop()
except:
    pass
stats = site_view.create_view('Stats',{
    'objid':stats,
    'where':stat_cols['parameter_cd'] == '00060'
})

stat_cols = dict((x['name'],x) for x in stats.columns())
    

try:
    site_view.View('CurrentDaily').drop()
except:
    pass
datatab = site_view.create_view('CurrentDaily',{
    'objid':site_view,
    'cols':['_adm-rowid']+[
        dcols['datetime'],dcols['value'],
        stat_cols['min_va'],stat_cols['mean_va'],stat_cols['max_va']
    ],
    'join':[
        (streamsdata,('_adm-rowid','=','_adm-rowid')),
        (stats,
            {'all':[
                (scols['site_no'] == stat_cols['site_no']),
                (extract(dcols['datetime'],'month') == stat_cols['month_nu']),
                (extract(dcols['datetime'],'day') == stat_cols['day_nu']),
            ]}
        )
    ],
},materialized=True)

indexall(datatab)

try:
    site_view.View('POR').drop()
except:
    pass
por = site_view.create_view('POR',{'objid':db.View('StreamPOR')})

try:
    site_view.View('CompositeData').drop()
except:
    pass
rdat = site_view.create_view('CompositeData',{'objid':db.View('CompositeData')})

try:
    site_view.View('CurrentMagnitude').drop()
except:
    pass
maxh = site_view.create_view('CurrentMagnitude',{'objid':db.View('StreamPeak2014')})
