import sys, os

sys.path.append('../../../../')
from apps.updater import *

dataPath = './import-data'

infiles = [(f,os.path.join(dataPath,f))
        for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.csv']

class SiteTable(UpdateFileTable):
    columns = [
        {'name':'ntwk','datatype':'Text','alias':'Site Network'},
        {'name':'state','datatype':'Text','alias':'State'},
        {'name':'site_name','datatype':'Text','alias':'Site Name'},
        {'name':'site_no','datatype':'Text','alias':'Site Number'},
        {'name':'ts','datatype':'Text'},
        {'name':'start','datatype':'Text','alias':'POR Start'},
        {'name':'lat','datatype':'Text','alias':'Lat'},
        {'name':'lon','datatype':'Text','alias':'Lon'},
        {'name':'elev','datatype':'Text','alias':'Elevation (ft)'},
        {'name':'county','datatype':'Text','alias':'County'},
        {'name':'huc','datatype':'Text','alias':'HUC'},
        {'name':'hucname','datatype':'Text','alias':'HUC Name'},
    ]
    
    def process_result(self,infile):
        header, rows = UpdateFileTable.process_result(self,infile)
        outrows = []
        for row in rows:
            row.insert(3,row[2].split('(')[1].replace(')',''))
            row[2] = row[2].split('(')[0]
            row.append(row[-1].split('(')[1].replace(')',''))
            row[-2] = row[-2].split('(')[0]
            outrows.append(row)
        return header,outrows
    
try:
    db = cloud.Database('WaterMgmt')
    upd = Updater(UpdateFileDatabase('WaterMgmt',infiles,SiteTable),db)
    upd.create()
except common.errors.RelationDoesNotExist:
    upd = Updater(UpdateFileDatabase('WaterMgmt',infiles,SiteTable))
    db = upd.create()
upd.update()

sites = db.Table('SnotelSites').select(['site_no','state'])

class SnotelTable(UpdateWebTable):
    """Encapsulate the unique character of a Snotel table."""
   
    columns = [
        {'name':'site_no','datatype':'Text','alias':'Site Number'},
        {'name':'date','datatype':'Text','alias':'Observation Date'},
        {'name':'swe','datatype':'Text','alias':'Snow Water Equivalent (in)'},
        {'name':'precip','datatype':'Text','alias':'Precipitation Accumulation (in)'},
        {'name':'airmax','datatype':'Text','alias':'Air Temperature Maximum (degF)'},
        {'name':'airmin','datatype':'Text','alias':'Air Temperature Minimum (degF)'},
        {'name':'airavg','datatype':'Text','alias':'Air Temperature Average (degF)'},
        {'name':'precipinc','datatype':'Text','alias':'Precipitation Increment (in)'},
    ]
    
    def __init__(self,name,url,site_no):
        self.site_no = site_no
        UpdateWebTable.__init__(self,name,url)
    
    def process_result(self,text):
        header,rows = UpdateWebTable.process_result(self,text)
        if header is None and rows is None:
            return None, None
        return header, [[self.site_no]+r for r in rows]

# Now the data itself
spec = []
for site_no,state in sites:
    url = "http://www.wcc.nrcs.usda.gov/reportGenerator/view_csv/customSingleStationReport/daily/{site_no}:{state}:SNTL%7Cid=%22%22%7Cname/POR_BEGIN,POR_END/WTEQ::value,PREC::value,TMAX::value,TMIN::value,TAVG::value,PRCP::value"
    spec.append(('SnotelData',url.format(**{
        'site_no':site_no,
        'state':state
    }),site_no))

data_u = Updater(UpdateWebDatabase('WaterMgmt',spec,SnotelTable), db)
data_u.create()
data_u.update()
