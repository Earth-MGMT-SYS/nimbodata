import sys, os

sys.path.append('../../../../')
from apps.updater import *

dataPath = './import-data'

if __name__ == '__main__':
    infiles = [(f,os.path.join(dataPath,f))
        for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.shp']
        
    try:
        db = cloud.Database('WaterMgmt')
        upd = Updater(
            UpdateShapefileDatabase(
                    'WaterMgmt',infiles,UpdateShapefileTable,'RiverSegments'
                ),db
        )
        upd.create()
    except common.errors.RelationDoesNotExist:
        upd = Updater(
            UpdateShapefileDatabase('WaterMgmt',
                infiles,
                UpdateShapefileTable,'RiverSegments')
        )
        db = upd.create()
    upd.update()
    
    table = db.Table('RiverSegments')
    result = table.select()
    print 'Rivers',len(result.rows)
