import sys, os

sys.path.append('../../')
from apps.updater import Updater, UpdateShapefileDatabase, UpdateShapefileTable

dataPath = './import-data'

if __name__ == '__main__':
    infiles = [(f,os.path.join(dataPath,f))
        for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.shp']
    
    a = Updater(
        UpdateShapefileDatabase('Colorado River',infiles,UpdateShapefileTable,'Segments')
    )
    
    a.create()
    a.update()
    
    table = a.db.Table('Segments')
    result = table.select()
    print 'Rivers',len(result.rows)
