
import sys, os

sys.path.append('../../../../')

from client import pyclient

from core.pg.datatypes import Text,Point,Date,Float
from common.expressions import simplify

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

h1, h2, h3 = db.Table('HUC2'), db.Table('HUC4'), db.Table('HUC6')
h4 = h5 = h3
#h4 = db.Table('HUC8')
#h5 = db.Table('HUC10')

try:
    db.View('HUC').drop()
except ValueError:
    pass
view = db.create_view('HUC',{'objid':db.Table('HUC6')})
#view = db.View('HUC')

sch = {}
for z in range(19):
    if z in range(0,6):
        base = h1
    elif z < 8:
        base = h2
    elif z < 10:
        base = h3
    elif z < 13:
        base = h4
    else:
        base = h5
    cols = base.columns()
    zvw = view.create_view('z'+str(z),{
        'objid':base,
        'cols':['_adm-rowid']+cols[:-1]+[simplify('geom',5/(3**float(z)))]
    },materialized=True)
    zvw.columns()[-1].modify({'name':'geom','alias':'geom'})
    for c in zvw.columns():
        zvw.add_index(c)
    sch[z] = zvw

view.modify({'dobj':{'tilescheme':sch}})





