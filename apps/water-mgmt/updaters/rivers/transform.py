
import sys, os

sys.path.append('../../../../')

from client import pyclient

from core.pg.datatypes import Text,Point,Date,Float

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

huc = db.Table('RiverSegments')
cols = dict((x['name'],x) for x in huc.columns())

cols['HUC'].modify({'datatype':'Float'})
cols['SEG'].modify({'datatype':'Integer'})
cols['SEQNO'].modify({'datatype':'Integer'})
