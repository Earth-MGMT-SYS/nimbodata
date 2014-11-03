import sys, os
from StringIO import StringIO

sys.path.append('../../../../')
from apps.updater import *

if __name__ == '__main__':
    
    db = cloud.Database('WaterMgmt')
    
    infiles = [
        ['NOAASnowForecast','ftp://ftp.hpc.ncep.noaa.gov/shapefiles/ww/day1/day1_psnow_gt_08_2013041900.tar']
    ]
    
    a = Updater(
        UpdateShapefileDatabase('WaterMgmt',infiles,UpdateShapefileZipURL),db
    )
    
    a.create()
    a.update()

    infiles = [
        ['NOAAPrecipPercent','http://water.weather.gov/precip/p_download_new/2014/11/01/nws_precip_year2date_percent_shape_20141101.tar.gz']
    ]
    
    a = Updater(
        UpdateShapefileDatabase('WaterMgmt',infiles,UpdateShapefileZipURL),db
    )
    
    a.create()
    a.update()
