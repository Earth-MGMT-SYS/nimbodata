
import sys, os

sys.path.append('../../../../')

from client import pyclient

from core.pg.datatypes import Text,Point,Date,Float

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

huc = db.Table('HUC2')
tmn,meta,src,srco,srcfeat,load,gnis,areaac,areakm,states,huc2,name,geom,leng,area, = \
    huc.columns()

states.modify({'datatype':'TextArray'})
tmn.drop()
meta.drop()
src.drop()
srco.drop()
srcfeat.drop()
load.drop()
gnis.drop()

#huc.add_index(geom)
