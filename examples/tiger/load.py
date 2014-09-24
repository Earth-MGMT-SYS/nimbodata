import sys, os
from StringIO import StringIO

sys.path.append('../../')
from apps.updater import Updater, UpdateShapefileDatabase, UpdateShapefileZipURL

dataPath = './import-data'

if __name__ == '__main__':
        
    infiles = [
        ['CongressionalDistricts','ftp://ftp2.census.gov/geo/tiger/TIGER2014/CD/tl_2014_us_cd114.zip'],
        ['USCoastline','ftp://ftp2.census.gov/geo/tiger/TIGER2014/COAST/tl_2014_us_coastline.zip'],
        #['USCoastline','file:///mnt/code/nimbodata/examples/tiger/import-data/tl_2014_us_coastline.zip'],
        ['Counties','ftp://ftp2.census.gov/geo/tiger/TIGER2014/COUNTY/tl_2014_us_county.zip'],
        ['MilitaryInstallations','ftp://ftp2.census.gov/geo/tiger/TIGER2014/MIL/tl_2014_us_mil.zip'],
        ['AZPlaces','ftp://ftp2.census.gov/geo/tiger/TIGER2014/PLACE/tl_2014_04_place.zip']
    ]
    
    a = Updater(
        UpdateShapefileDatabase('TigerLine',infiles,UpdateShapefileZipURL)
    )
    
    a.create()
    a.update()
    
        
