import sys, os

sys.path.append('../../../../')
from common.expressions import unique
from apps.updater import *

dataPath = './import-data'

infiles = [(f,os.path.join(dataPath,f))
        for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.csv']

class SiteTable(UpdateFileTable):
    columns = [
        {'name':'site_no','datatype':'Text','alias':'Site Number'},
        {'name':'RiverBasin','datatype':'Text','alias':'HUC Name'},
        {'name':'site_name','datatype':'Text','alias':'Site Name'},
        {'name':'elev','datatype':'Text','alias':'Elevation (m)'},
        {'name':'lat','datatype':'Text','alias':'Lat'},
        {'name':'lon','datatype':'Text','alias':'Lon'},
        {'name':'start','datatype':'Text','alias':'POR Start'},
        {'name':'end','datatype':'Text','alias':'POR End'},
        {'name':'status','datatype':'Text','alias':'Status'}        
    ]
    
    def process_result(self,infile):
        header, rows = UpdateFileTable.process_result(self,infile)
        outrows = []
        for row in rows:
            row[4] = int(row[4][:2]) + float(row[4][-2:-1])/60
            row[5] = (-1 * int(row[5][:3])) + float(row[5][-2:-1])/60
            outrows.append(row)
        return self.columns,outrows

try:
    db.Table('BCRFCSites').drop()
except:
    pass

try:
    db = cloud.Database('WaterMgmt')
    upd = Updater(UpdateFileDatabase('WaterMgmt',infiles,SiteTable),db)
    upd.create()
except common.errors.RelationDoesNotExist:
    upd = Updater(UpdateFileDatabase('WaterMgmt',infiles,SiteTable))
    db = upd.create()
upd.update()

sites = db.Table('BCRFCSites').select(['site_no'])

class BCRFCTable(UpdateZipWebTable):
    """Encapsulate the unique character of a BCRFC csv."""
   
    columns = [
        {'name':'site_no','datatype':'Text','alias':'Site Number'},
        {'name':'date','datatype':'Text','alias':'Observation Date'},
        {'name':'airmax','datatype':'Text','alias':'Air Temperature Maximum (degF)'},
        {'name':'airmaxcode','datatype':'Text'},
        {'name':'airmin','datatype':'Text','alias':'Air Temperature Minimum (degF)'},
        {'name':'airmincode','datatype':'Text'},
        {'name':'precipinc','datatype':'Text','alias':'Precipitation Increment (in)'},
        {'name':'precipinccode','datatype':'Text'},
        {'name':'precipacc','datatype':'Text','alias':'Precipitation Accumulated (in)'},
        {'name':'precipacccode','datatype':'Text'},
        {'name':'swe','datatype':'Text','alias':'Snow Water Equivalent (in)'},
        {'name':'swecode','datatype':'Text'},
        {'name':'snowdepth','datatype':'Text','alias':'Snow Depth (in)'},
        {'name':'snowdepthcode','datatype':'Text'},
    ]
    
    def __init__(self,name,url,site_no):
        print site_no, url
        self.site_no = site_no
        UpdateZipWebTable.__init__(self,name,url)
    
    def process_result(self,text):
        text = '\n'.join(text.split('\n')[9:])
        header,rows = UpdateZipWebTable.process_result(self,text)
        if len(header) < len(self.columns):
            appender = (len(self.columns) - len(header)) * [None]
        else:
            appender = None
        if header is None and rows is None:
            return None, None
        if appender is not None:
            return self.columns, [x+appender for x in rows]
        
        def goodrow(row):
            try:
                return int(x[1].split('-')[0]) > 0
            except ValueError:
                return False
        return self.columns, [x for x in rows if goodrow(x)]

try:
    db.Table('BCRFCData').drop()
except:
    pass

# Now the data itself
spec = []
for site_no in sites:
    url = "http://bcrfc.env.gov.bc.ca/data/asp/archive/{site_no}.zip"
    spec.append(('BCRFCData',url.format(**{
        'site_no':site_no[0],
    }),site_no))

data_u = Updater(UpdateWebDatabase('WaterMgmt',spec,BCRFCTable), db)
data_u.create()
data_u.update()
