
import sys, os

sys.path.append('../../../../')

from client import pyclient

from core.pg.datatypes import Text,Point,Date,Float

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('SnotelSites')
cols = dict((x['name'],x) for x in site_table.columns())
elev, lon, lat, start = cols['elev'],cols['lon'],cols['lat'],cols['start']
snum = cols['site_no']

elev.modify({'datatype':'Integer'})
lon.modify({'datatype':'Float'})
lat.modify({'datatype':'Float'})
start.modify({'datatype':'Date','exp':'YYYY-Month-01'})

site_table.add_index(snum)

site_table.add_columns([
    {'name':'geom','datatype':Point,'exp':Point(lon,lat)},
])

data_table = db.Table('SnotelData')
snum,obd,swe,pre,tma,tmi,tav,pri = data_table.columns()

obd.modify({'datatype':'Date','exp':'YYYY-MM-DD'})
swe.modify({'datatype':'Float'})
pre.modify({'datatype':'Float'})
tma.modify({'datatype':'Integer'})
tmi.modify({'datatype':'Integer'})
tav.modify({'datatype':'Integer'})
pri.modify({'datatype':'Float'})

data_table.add_index(snum)
data_table.add_index(obd)
data_table.add_index(swe)
