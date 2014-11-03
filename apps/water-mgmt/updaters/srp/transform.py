
import sys, os

sys.path.append('../../../../')
from client import pyclient
from core.pg.datatypes import Text,Point,Date,Float

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('SRPReservoirs')

siteid,sitename,rb,county,lon,lat,elev,oper,capacity = site_table.columns()

elev.modify({'datatype':'Float'})
lon.modify({'datatype':'Float'})
lon.modify({'alias':'Latitude'})
lat.modify({'datatype':'Float'})
lat.modify({'alias':'Longitude'})
capacity.modify({'datatype':'Float'})
site_table.add_columns([
    {'name':'geom','datatype':Point,'exp':Point(lon,lat)},
])

data_table = db.Table('SRPResData')

siteid, date, elev, content = data_table.columns()

date.modify({'alias':'Date','datatype':'Date','exp':'YYYY-MM-DD'})
content.modify({'alias':'Reservoir Content (af)','datatype':'Float'})
elev.modify({'datatype':'Float'})

data_table.add_index(date)
data_table.add_index(content)
data_table.add_index(elev)
data_table.add_index(siteid)

