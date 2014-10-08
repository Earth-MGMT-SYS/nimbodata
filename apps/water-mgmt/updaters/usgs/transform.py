
import sys, os

sys.path.append('../../../../')
from client import pyclient
from core.pg.datatypes import Text,Point,Date,Float

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('USGSSites')

cols = dict((x['name'],x) for x in site_table.columns())
lon, lat = cols['dec_long_va'],cols['dec_lat_va']
lonf, latf = cols['long_va'],cols['lat_va']

lon.modify({'datatype':'Float'})
lat.modify({'datatype':'Float'})
lonf.modify({'datatype':'Float'})
latf.modify({'datatype':'Float'})

site_table.add_columns([
    {'name':'geom','datatype':Point,'exp':Point(lon,lat)},
])

site_table.add_index(cols['site_no'])
site_table.add_index(cols['geom'])

data_table = db.Table('USGSData')

cols = dict((x['name'],x) for x in data_table.columns())
val,dt = cols['value'],cols['datetime']


val.modify({'datatype':'Float'})
dt.modify({'datatype':'Date','exp':'YYYY-MM-DD'})

data_table.add_index(dt)
data_table.add_index(cols['site_no'])
data_table.add_index(cols['statcode'])
data_table.add_index(cols['parameter_cd'])
data_table.add_index(cols['value'])


stat_table = db.Table('USGSStats')
stat_cols = dict((x['name'],x) for x in stat_table.columns())

stat_cols['agency_cd'].drop()
stat_cols['loc_web_ds'].drop()
stat_cols['month_nu'].modify({'datatype':'Integer','alias':'Month','name':'month'})
stat_cols['day_nu'].modify({'datatype':'Integer','alias':'Day','name':'day'})

stat_cols['begin_yr'].modify({'datatype':'Integer','alias':'Begin Year'})
stat_cols['end_yr'].modify({'datatype':'Integer','alias':'End Year'})
stat_cols['count_nu'].modify({'datatype':'Integer'})
stat_cols['max_va_yr'].modify({'datatype':'Integer','alias':'Max Value Year'})
stat_cols['min_va_yr'].modify({'datatype':'Integer','alias':'Min Value Year'})
stat_cols['max_va'].modify({'datatype':'Float','alias':'Max Value'})
stat_cols['min_va'].modify({'datatype':'Float','alias':'Min Value'})
stat_cols['mean_va'].modify({'datatype':'Float','alias':'Mean Value'})

stat_table.add_index(stat_cols['site_no'])
stat_table.add_index(stat_cols['parameter_cd'])
