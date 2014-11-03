
import sys, os

sys.path.append('../../../../')
from client import pyclient
from core.pg.datatypes import Text,Point,Date,Float

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('BORReservoirs')

dam,lake,lkid,lat,lon,maxtor,maxelev = site_table.columns()

dam.modify({'alias':'Dam Name'})
lake.modify({'alias':'Lake Name'})
lkid.modify({'alias':'Lake ID'})
maxtor.modify({'datatype':'Float','alias':'Maximum Elevation (ft asl)'})
maxelev.modify({'datatype':'Float'})
lon.modify({'datatype':'Float'})
lon.modify({'alias':'Dam Latitude'})
lat.modify({'datatype':'Float'})
lat.modify({'alias':'Dam Longitude'})
site_table.add_columns([
    {'name':'geom','datatype':Point,'exp':Point(lon,lat)},
])

data_table = db.Table('LCResData')

date, site_name, elev, content, release = data_table.columns()

date.modify({'alias':'Date','datatype':'Date','exp':'YYYY-MM-DD'})
elev.modify({'alias':'Pool Elevation (ft asl)','datatype':'Float'})
content.modify({'alias':'Content (kaf)','datatype':'Float'})
release.modify({'alias':'Release (cfs)','datatype':'Float'})

data_table.add_index(date)
data_table.add_index(content)
data_table.add_index(release)
data_table.add_index(elev)
