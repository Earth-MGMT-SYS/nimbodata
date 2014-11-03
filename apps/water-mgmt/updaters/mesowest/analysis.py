
import sys, os
from pprint import pprint

sys.path.append('../../../../')
from client import pyclient
from core.pg.datatypes import Text,Point,Date,Float
from common.expressions import extract,MIN,MAX,AVG,count,unique,Join
user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

cloud = pyclient.connect('http://localhost:5000',user)

db = cloud.Database('WaterMgmt')

site_table = db.Table('CDECReservoirs')
site_cols = dict((x['name'],x) for x in site_table.columns())

data_table = db.Table('CDECResData')
data_cols = dict((x['name'],x) for x in data_table.columns())
dt = data_cols['date']

def indexall(rel):
    for col in rel.columns():
        rel.add_index(col)
    try:
        rel.add_index('_adm-rowid')
    except ValueError:
        pass

try:
    db.View('Reservoirs2014Data').drop()
except:
    pass
resdata = db.create_view('Reservoirs2014Data',{
    'objid':site_table,
    'where':[dt >= Date(2013,10,1),dt < Date(2014,10,1)],
    'join':Join(data_table),
},materialized=True)

try:
    db.View('Reservoirs2014Sites').drop()
except:
    pass
siteid_view = db.create_view('Reservoirs2014Sites',{
    'objid':resdata,
    'cols':[unique(site_cols['StationID'])]
},materialized=True)

indexall(siteid_view)

try:
    db.View('Reservoirs2014').drop()
except:
    pass
site_view = db.create_view('Reservoirs2014',{
    'objid':site_table,
    'cols':['_adm-rowid']+site_table.columns(),
    'join':(siteid_view,('StationID','=','unique(StationID)')),
},materialized=True)

indexall(site_view)

try:
    db.View('ReservoirPOR').drop()
except:
    pass
sitestart = db.create_view('ReservoirPOR',{
    'objid':site_table,
    'cols':['_adm-rowid',MIN(dt),MAX(dt),count(dt),site_cols['geom']],
    'join':(data_table,('StationID','=','StationID')),
    'group_by':['_adm-rowid',site_cols['geom']]
},materialized=True)

indexall(sitestart)

data_cols = dict((x['name'],x) for x in data_table.columns())

try:
    db.View('ReservoirPeak2014').drop()
except:
    pass
peak2014 = db.create_view('ReservoirPeak2014',{
    'objid':site_table,
    'cols':['_adm-rowid']+[data_cols['StationID'],MAX(data_cols['content'])],
    'where':[dt >= Date(2013,10,1),dt < Date(2014,10,1)],
    'join':(data_table,('StationID','=','StationID')),
    'group_by':['_adm-rowid','StationID']+[data_cols['StationID']]
},materialized=True)

indexall(peak2014)


site_view = db.View('Reservoirs2014')
maxres = db.Table('CDECResInfo')
maxcols = dict((x['name'],x) for x in maxres.columns())

try:
    db.View('ReservoirMaxHistorical').drop()
except:
    pass
maxhist = db.create_view('ReservoirMaxHistorical',{
    'objid':site_table,
    'cols':['_adm-rowid']+['StationID','Capacity'],
    'join':(maxres,('StationID','=','StationID')),
    'order_by':[maxcols['StationID']]
},materialized=True)

indexall(maxhist)


site_view = db.View('Reservoirs2014')
maxhist = db.View('ReservoirMaxHistorical')
peak2014 = db.View('ReservoirPeak2014')
resdata = db.View('Reservoirs2014Data')


hcols = dict((x['name'],x) for x in maxhist.columns())
ycols = dict((x['name'],x) for x in peak2014.columns())

try:
    db.View('ReservoirData').drop()
except:
    pass
datatab = db.create_view('ReservoirData',{
    'objid':maxhist,
    'cols':['_adm-rowid']+[Float(ycols['MAX(CDECResData.content)']),Float(hcols['Capacity'])],
    'join':Join(peak2014,('StationID','=','StationID'))
},materialized=True)

indexall(datatab)

content,capacity = datatab.columns()

try:
    db.View('Reservoirs').drop()
except:
    pass
site_view = db.create_view('Reservoirs',{
    'objid':datatab,
    'cols':['_adm-rowid'] + site_view.columns()[:-1] + [content / capacity, 'geom'],
    'join':Join(site_view,('_adm-rowid','=','_adm-rowid'))
},materialized=True)

indexall(datatab)

site_view.columns()[-2].modify({'name':'magnitude','alias':'Proportion of Capacity'})

dcols = dict((x['name'],x) for x in resdata.columns())
scols = dict((x['name'],x) for x in site_view.columns())

try:
    site_view.View('Daily2014').drop()
except:
    pass
datatab = site_view.create_view('Daily2014',{
    'objid':resdata,
    'cols':['_adm-rowid']+[dcols['date'],dcols['content']],
    'order_by':['StationID']
},materialized=True)

indexall(datatab)

try:
    site_view.View('POR').drop()
except:
    pass
por = site_view.create_view('POR',{'objid':db.View('ReservoirPOR')})

try:
    site_view.View('Data').drop()
except:
    pass
rdat = site_view.create_view('Data',{'objid':db.View('ReservoirData')})

try:
    site_view.View('MaxHistorical').drop()
except:
    pass
maxh = site_view.create_view('MaxHistorical',{'objid':db.View('ReservoirMaxHistorical')})

try:
    site_view.View('Peak2014').drop()
except:
    pass
maxh = site_view.create_view('Peak2014',{'objid':db.View('ReservoirPeak2014')})
