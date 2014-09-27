
import sys, os

sys.path.append('../../../../')

from client import pyclient
import client_config as cfg

from core.pg.datatypes import Text,Point,Date

cloud = pyclient.connect('http://localhost:5000',cfg.user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('sites')

site_table.add_columns([
    {'name':'startdate','datatype':Date},
    {'name':'geom','datatype':Point},
])

for row in site_table:
    
