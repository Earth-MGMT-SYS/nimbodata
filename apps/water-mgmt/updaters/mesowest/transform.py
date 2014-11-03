
import sys, os

sys.path.append('../../../../')
from client import pyclient
from core.pg.datatypes import Text,Point,Date,Float

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('CDECReservoirs')

siteid,sitename,rb,county,lon,lat,elev,oper = site_table.columns()

lon.modify({'datatype':'Float'})
lon.modify({'alias':'Latitude'})
lat.modify({'datatype':'Float'})
lat.modify({'alias':'Longitude'})
site_table.add_columns([
    {'name':'geom','datatype':Point,'exp':Point(lon,lat)},
])

data_table = db.Table('CDECResData')

siteid, date, content = data_table.columns()

date.modify({'alias':'Date','datatype':'Date','exp':'YYYY-MM-DD'})
content.modify({'alias':'Reservoir Content (af)','datatype':'Integer'})

data_table.add_index(date)
data_table.add_index(content)
data_table.add_index(siteid)

max_table = db.Table('CDECResInfo')

mstid, cap = max_table.columns()

cap.modify({'alias':'Reservoir Capacity (af)','datatype':'Integer'})
