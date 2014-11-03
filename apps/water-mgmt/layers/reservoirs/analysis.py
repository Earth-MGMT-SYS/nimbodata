"""Process the various reservoir data sources."""
import sys, os
from pprint import pprint

sys.path.append('../../../../')
from client import pyclient
from core.pg.datatypes import Text,Point,Date,Float
from common.expressions import extract,MIN,MAX,AVG,count,unique,Join,Union

import apps.analyze.timeseries as atime

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

# First we're going to get a similar view of each base site and data table.
cdec_site_table = db.Table('CDECReservoirs')
cdec_site_cols = dict((x['name'],x) for x in cdec_site_table.columns())
cdec_site_info = db.Table('CDECResInfo')
sid, snm, rb, county, lat, lon, elev, op, geom = cdec_site_table.columns()
ssid, cap = cdec_site_info.columns()

try:
    db.View('CDECReservoirs').drop()
except:
    pass
cdec_site_view = db.create_view('CDECReservoirs', {
    'objid':cdec_site_table,
    'cols':[snm, ssid, lat, lon, elev, cap / 1000, geom],
    'join':Join(cdec_site_info)
})

cdec_data_table = db.Table('CDECResData')
cdec_data_cols = dict((x['name'],x) for x in cdec_data_table.columns())
sid, dt, cont = cdec_data_table.columns()
dt = cdec_data_cols['date']

try:
    db.View('CDECResData').drop()
except:
    pass
cdec_data_view = db.create_view('CDECResData',{
    'objid':cdec_data_table,
    'cols':[sid, dt, cont / 1000]
})

bor_site_table = db.Table('BORReservoirs')
dam,lake,lakeid,lon,lat,maxstor,maxelev,geom = bor_site_table.columns()
bor_data_table = db.Table('LCResData')
dt, sid, elev, cont, release = bor_data_table.columns()

try:
    db.View('BORReservoirs').drop()
except:
    pass
bor_site_view = db.create_view('BORReservoirs', {
    'objid':bor_site_table,
    'cols':[lake,lakeid,lat,lon,maxelev,maxstor,geom]
})

try:
    db.View('LCResData').drop()
except:
    pass
bor_data_view = db.create_view('LCResData', {
    'objid':bor_data_table,
    'cols':[sid, dt, cont]
})

try:
    db.View('LCResData').drop()
except:
    pass
bor_data_view = db.create_view('LCResData', {
    'objid':bor_data_table,
    'cols':[sid, dt, cont]
})

srp_site_table = db.Table('SRPReservoirs')
srp_site_cols = dict((x['name'],x) for x in srp_site_table.columns())
sid, snm, rb, county, lat, lon, maxelev, op, maxstor, geom = srp_site_table.columns()
srp_data_table = db.Table('SRPResData')
ssid, dt, elev, cont = srp_data_table.columns()

try:
    db.View('SRPReservoirs').drop()
except:
    pass
srp_site_view = db.create_view('SRPReservoirs', {
    'objid':srp_site_table,
    'cols':[snm, sid, lat, lon, maxelev, maxstor / 1000, geom]
})

try:
    db.View('SRPResData').drop()
except:
    pass
srp_data_view = db.create_view('SRPResData', {
    'objid':srp_data_table,
    'cols':[ssid, dt, cont / 1000]
})

# Now that we have views with the same signature, we can create our unions.
try:
    db.View('ReservoirSites').drop()
except:
    pass
qa, qb, qc = {'objid':bor_site_view}, {'objid':cdec_site_view}, {'objid':srp_site_view}
site_table = db.create_view('ReservoirSites',Union(qa,qb,qc))

try:
    db.View('ReservoirData').drop()
except:
    pass
qa, qb, qc = {'objid':bor_data_view}, {'objid':cdec_data_view}, {'objid':srp_data_view}
data_table = db.create_view('ReservoirData',Union(qa,qb,qc))


site_cols = site_table.columns()
site_cols[1].modify({'name':'siteid'})
data_cols = data_table.columns()
data_cols[0].modify({'name':'siteid'})
data_cols[2].modify({'name':'value'})

# Because we want to use capacity instead of actual max, provide a stat table.
try:
    db.View('ReservoirStats').drop()
except:
    pass
daily_stats = db.create_view('ReservoirStats',{
    'objid':site_table,
    'cols':['_adm-rowid']+[site_cols[1],
        extract(data_cols[1],'month'),extract(data_cols[1],'day'),
        MIN(data_cols[2]),AVG(data_cols[2]),'maxstorage'
    ],
    'join':Join(data_table),
    'group_by':['_adm-rowid',site_cols[1],extract(data_cols[1],'month'),
        extract(data_cols[1],'day'),'maxstorage'
    ]
})

# Now we hand it off to analyze timeseries, which will construct the views.
reslayer = atime.make_site_timeseries_views(
    db,'Reservoirs',site_table,data_table,daily_stats,'maximum'
)

