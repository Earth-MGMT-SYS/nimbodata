import sys, os

sys.path.append('../../../../')
from apps.updater import Updater, UpdateFileDatabase, UpdateFileTable

dataPath = './import-data'

if __name__ == '__main__':
    infiles = [(f,os.path.join(dataPath,f))
        for f in os.listdir(dataPath) if os.path.splitext(f)[1] == '.csv']
    
    a = Updater(UpdateFileDatabase('WaterMgmt',infiles,UpdateFileTable))
    a.create()
    a.update()
