"""Process Snow data into a set of timeseries views."""

import sys, os
import datetime

sys.path.append('../../../../')

from client import pyclient

from common.datatypes import Text,Point,Date,Float
from common.expressions import extract,MIN,MAX,AVG,count,unique,Join,Union, AS

import apps.analyze.timeseries as atime

def indexall(rel):
    for col in rel.columns():
        rel.add_index(col)
    try:
        rel.add_index('_adm-rowid')
    except ValueError:
        pass

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

# Getting references to work with.
snotel_site_table = db.Table('SnotelSites')
snotel_site_cols = dict((x['name'],x) for x in snotel_site_table.columns())
snam, ssnum = snotel_site_cols['site_name'], snotel_site_cols['site_no']

snotel_data_table = db.Table('SnotelData')
snum,obd,swe,pre,tma,tmi,tav,pri = snotel_data_table.columns()

bcrfc_site_table = db.Table('BCRFCSites')
bcrfc_site_cols = dict((x['name'],x) for x in bcrfc_site_table.columns())

bcrfc_data_table = db.Table('BCRFCData')
bcrfc_data_cols = dict((x['name'],x) for x in bcrfc_data_table.columns())

# Setting up the subqueries for sites.
qa = {
    'objid':snotel_site_table,
    'cols':[ssnum,snam,snotel_site_cols['elev'],snotel_site_cols['huc'],
        snotel_site_cols['geom']
    ],
}
qb = {
    'objid':bcrfc_site_table,
    'cols':[bcrfc_site_cols['site_no'],bcrfc_site_cols['site_name'],
        bcrfc_site_cols['elev'],
        bcrfc_site_cols['RiverBasin'],
        bcrfc_site_cols['geom']
    ]
}
try: db.View('SnowSites').drop()
except: pass
site_table = db.create_view('SnowSites',Union(qa,qb))

# The subqueries for data.
qa = {
    'objid':snotel_data_table,
    'cols':[snum,obd,swe]
}
qb = {
    'objid':bcrfc_data_table,
    'cols':['site_no','date','swe']
}
try: db.View('SnowData').drop()
except: pass
data_table = db.create_view('SnowData', Union(qa,qb))

# Modify to fit the naming convention for timeseries module.
site_cols = site_table.columns()
site_cols[0].modify({'name':'siteid'})
data_cols = data_table.columns()
data_cols[0].modify({'name':'siteid'})
data_cols[2].modify({'name':'value'})

# Pass it off to the timeseries module.
layer = atime.make_site_timeseries_views(db,'Snow',site_table,data_table)

