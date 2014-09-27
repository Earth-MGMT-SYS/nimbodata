"""Do not use - reference use only"""

import sys, os
import csv
import datetime
import StringIO

import requests

sys.path.append('../../core')

import cloud_controller as cc

cloud = cc.Cloud()

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

try:
    db = cloud.create_db('USGS',user)
except cc.IntegrityError:
    db = cloud.get_dbid('USGS',user)

def get_usgsdata(url):
    r = requests.get(url)
    f = StringIO.StringIO(r.text)
    reader = csv.reader((x for x in f if not x.startswith('#')), dialect='excel-tab')

    try:
        header = next(reader)
        lengths = next(reader)
    except:
        #print r.text
        return None

    cols = [{'colname':x.lower(),'dtype':'text'} for x in header]
    return cols,reader

def get_parametercodes():
    url = "http://nwis.waterdata.usgs.gov/usa/nwis/pmcodes?radio_pm_search=param_group&pm_group=All+--+include+all+parameter+groups&pm_search=&casrn_search=&srsname_search=&format=rdb&show=parameter_group_nm&show=parameter_nm&show=casrn&show=srsname&show=parameter_units"
    cols, reader = get_usgsdata(url)
    
    try:
        table = cloud.create_table(db,'USGS Parameters',user,cols)
    except cc.IntegrityError:
        cloud.drop_table(cloud.get_tblid(db,'USGS Parameters',user))
        table = cloud.create_table(db,'USGS Parameters',user,cols)
     
    for i,row in enumerate(reader):
        outRow = [x if x != '' else None for x in row]
        cloud.insert(table,outRow)
        if i % 100 == 0:
            print i
            
def create_datatable():
    cols = [
        {'colname':'site_no','dtype':'text','colalias':'Site Number'},
        {'colname':'datetime','dtype':'date','colalias':'Observation Date'},
        {'colname':'value','dtype':'real','colalias':'Observation Value'},
        {'colname':'valcode','dtype':'text','colalias':'Value Status Code'},
        {'colname':'valparam','dtype':'text','colalias':'Value Parameter Code'},
        {'colname':'valstat','dtype':'text','colalias':'Value Statistic Code'}
    ]
    try:
        datatable = cloud.create_table(db,'USGS Data',user,cols)
    except cc.IntegrityError:
        cloud.drop_table(cloud.get_tblid(db,'USGS Data',user))
        datatable = cloud.create_table(db,'USGS Data',user,cols)
    return datatable
    
def create_statstable():
    cols = [
        {'colname':'agency_cd','dtype':'text','colalias':'Agency Code'},
        {'colname':'site_no','dtype':'text','colalias':'Site Number'},
        {'colname':'parameter_cd','dtype':'text','colalias':'Parameter Code'},
        {'colname':'loc_web_ds','dtype':'text','colalias':'Location Web Datasource'},
        {'colname':'dd_nu','dtype':'integer','colalias':'DD Number'},
        {'colname':'month_nu','dtype':'integer','colalias':'Month Number'},
        {'colname':'day_nu','dtype':'integer','colalias':'Day Number'},
        {'colname':'begin_yr','dtype':'integer','colalias':'Begin Year'},
        {'colname':'end_yr','dtype':'integer','colalias':'End Year'},
        {'colname':'count_nu','dtype':'integer','colalias':'Count Number'},
        {'colname':'max_va_yr','dtype':'integer','colalias':'Max Value Year'},
        {'colname':'max_va','dtype':'real','colalias':'Max Value'},
        {'colname':'min_va_yr','dtype':'integer','colalias':'Min Value Year'},
        {'colname':'min_va','dtype':'real','colalias':'Min Value'},
        {'colname':'mean_va','dtype':'real','colalias':'Mean Value'}
    ]
    try:
        statstable = cloud.create_table(db,'USGS Stats',user,cols)
    except cc.IntegrityError:
        cloud.drop_table(cloud.get_tblid(db,'USGS Stats',user))
        statstable = cloud.create_table(db,'USGS Stats',user,cols)
    return statstable

def get_siteinfo(url,sitetable=None,datatable=None,statstable=None,
        get_data=False,get_stats=False):        
    if datatable is None:
        datatable = create_datatable()
    if statstable is None:
        statstable = create_statstable()
    
    cols, reader = get_usgsdata(url)
    
    cols[6]['dtype'] = 'float'
    cols[7]['dtype'] = 'float'
    cols[19]['dtype'] = 'float'
    cols[-3]['dtype'] = 'float'
    cols[-4]['dtype'] = 'float'
    cols[-12]['dtype'] = 'float'
    cols[-13]['dtype'] = 'float'
    cols += [{'colname':'location','dtype':'geography(POINT,4326)'}]
    
    sitecode_col = [i for i,x in enumerate(cols) 
        if x['colname'] == 'site_no'][0]
        
    alias_cols = dict((('site_no','Site Number'),('station_nm','Station Name'),
     ('site_tp_cd','Site Type Code'),('alt_va','Altitude (ft)')))
     
    for col in cols:
        if col['colname'] in alias_cols:
            col['colalias'] = alias_cols[col['colname']]
    
    if sitetable is None:
        try:
            sitetable = cloud.create_table(db,'USGS Sites',user,cols)
        except cc.IntegrityError:
            cloud.drop_table(cloud.get_tblid(db,'USGS Sites',user))
            sitetable = cloud.create_table(db,'USGS Sites',user,cols)
    
    for i,row in enumerate(reader):
        if get_data and get_site_data(row[sitecode_col],datatable) is None:
            continue
        get_site_stats(row[sitecode_col],statstable)
        
        outRow = [x if x != '' else None for x in row]
        outRow.append('POINT('+str(row[7])+' '+str(row[6])+')')       
        try:
            cloud.insert(sitetable,outRow)
        except:
            print row[7],row[6]
            continue
        
        print "Site ", i
    
    return sitetable,datatable,statstable
    
            
def create_site_view():
    table = cloud.get_tblid(db,'USGS Sites',user)
    cloud.create_view(db,'USGS Sites',user,{
        'viewid':table,
        'cols':['site_no','station_nm','site_tp_cd','alt_va','location']
    })
        
def create_this_wateryear():
    table = cloud.get_tblid(db,'USGS Data',user)
    cloud.create_view(db,'This Water Year',user,{
        'viewid':table
    })

def get_site_stats(sitecode,statstable):
    url = "http://waterservices.usgs.gov/nwis/stat/?format=rdb&sites=%(sitecode)s&statReportType=daily&statTypeCd=all"
    url = url % {
        'sitecode':sitecode
    }
    
    try:
        usgsdata = get_usgsdata(url)
        if usgsdata is None:
            return
        cols, reader = usgsdata
    except TypeError:
        return
    
    for i,row in enumerate(reader):
        cloud.insert(statstable,row[:15])


def get_site_data(sitecode,datatable):    
    url = "http://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=%(sitecode)s&startDT=2013-10-01&endDT=%(today)s"
    url = url % {
        'sitecode':sitecode,
        'today':datetime.date.today()
    }
        
    try:
        usgsdata = get_usgsdata(url)
        if usgsdata is None:
            return
        cols, reader = usgsdata
    except TypeError:
        return
    
    inval = iter(cols[3:])
    
    split_col = lambda x: x.split('_')[1:3]
    
    val_cols = []
    for i in range(len(cols[3:]) / 2):
        try:
            valparam, valstat = split_col(next(inval)['colname'])
        except ValueError:
            print sitecode, cols[3:]
            return
    
    for i,row in enumerate(reader):
        proc_row = [x if x != '' else None for x in row]
        row_stub = proc_row[1:3]
        vals = iter(proc_row[3:])
        for j in range(len(row[3:]) / 2):
            outRow = list(row_stub)
            outRow.append(next(vals))
            outRow.append(next(vals))
            outRow += [valparam,valstat]
        
            try:
                cloud.insert(datatable,outRow)
            except Exception as e:
                print row
                raise e

        if i % 100 == 0 and i != 0:
            print "Row ", i
    return True

def import_stats_codes():
    reader = csv.reader(open('statscodes.csv','rb'))
    header = next(reader)
    
    cols = [{'colname':x.replace(' ',''),'dtype':'text'} for x in header]
    
    try:
        table = cloud.create_table(db,'USGS Stats Codes',user,cols)
    except cc.IntegrityError:
        cloud.drop_table(cloud.get_tblid(db,'USGS Stats Codes',user))
        table = cloud.create_table(db,'USGS Stats Codes',user,cols)
    
    for i,row in enumerate(reader):
        outRow = [x if x != '' else None for x in row]
        stat_code_len = len(outRow[0])
        numzeros = 5 - stat_code_len
        outRow[0] = ''.join((['0'] * numzeros) + [x for x in outRow[0]])
        try:
            cloud.insert(table,outRow)
        except Exception as e:
            print row
            raise e
        if i % 100 == 0:
            print i

    

if __name__ == '__main__':
    #import_stats_codes()
    #get_parametercodes()
    url = "http://waterservices.usgs.gov/nwis/site/?format=rdb&siteType=ST&stateCd=co&siteOutput=expanded&hasDataTypeCd=dv&parameterCd=00060"
    sitetable,datatable,statstable = get_siteinfo(url,get_data=True,get_stats=True)
    create_site_view()
    for st in ('az','nm','tx','ca','or','wa','ut','wy','mt','id'):
        url = "http://waterservices.usgs.gov/nwis/site/?format=rdb&siteType=ST&stateCd=%(st)s&siteOutput=expanded&hasDataTypeCd=dv&parameterCd=00060" % {'st':st }
        get_siteinfo(url,sitetable,datatable,statstable,get_data=True,get_stats=True)
    #create_this_wateryear()
    
    
