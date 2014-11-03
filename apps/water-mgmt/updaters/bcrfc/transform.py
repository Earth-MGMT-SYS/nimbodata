
import sys, os

sys.path.append('../../../../')

from client import pyclient

from core.pg.datatypes import Text,Point,Date,Float

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('BCRFCSites')
cols = dict((x['name'],x) for x in site_table.columns())
elev, lon, lat = cols['elev'],cols['lon'],cols['lat']
start, end = cols['start'], cols['end']
snum = cols['site_no']

elev.modify({'datatype':'Integer'})
start.modify({'datatype':'Integer'})
end.modify({'datatype':'Integer'})
lon.modify({'datatype':'Float'})
lat.modify({'datatype':'Float'})

site_table.add_index(snum)

site_table.add_columns([
    {'name':'geom','datatype':Point,'exp':Point(lon,lat)},
])

data_table = db.Table('BCRFCData')
cols = dict((x['name'],x) for x in data_table.columns())
snum, obd, swe = cols['site_no'], cols['date'], cols['swe']
pre, pri, tma, tmi = cols['precipacc'], cols['precipinc'], cols['airmax'], cols['airmin']

obd.modify({'datatype':'Date','exp':'YYYY-MM-DD'})
swe.modify({'datatype':'Float'})
pre.modify({'datatype':'Float'})
tma.modify({'datatype':'Float'})
tmi.modify({'datatype':'Float'})
pri.modify({'datatype':'Float'})

data_table.add_index(snum)
data_table.add_index(obd)
data_table.add_index(swe)
