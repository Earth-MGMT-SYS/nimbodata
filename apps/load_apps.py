
import os
import sys

target = 'local'
user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'

if target == 'local':
    import nimbodata.cloud as cc
    cloud = cc.Cloud(user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",user)


for d in os.walk('.').next()[1]:
    try:        
        with open(os.path.join('.',d,'app.json'),'r') as f:
            appjson = f.read()
        with open(os.path.join('.',d,'app.css'),'r') as f:
            appcss = f.read()
    except IOError:
        continue
    
    try:
        db = cloud.create_database(d)
    except cc.RelationExists:
        cloud.Database(d).drop()
        db = cloud.create_database(d)
    
    table = db.create_table('assets',[
        {'name':'name','datatype':'Text'},
        {'name':'value','datatype':'Text'}
    ])

    table.insert(['app.json',appjson])
    table.insert(['app.css',appcss])

    
