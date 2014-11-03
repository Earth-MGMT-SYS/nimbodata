import json

import ogr,osr,os,sys
from gdalconst import *

sys.path.append('../../../../')

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'
import core.cloud as cc
cloud = cc.Cloud(user)


try:
    db = cloud.Database('WaterMgmt')
except cc.RelationDoesNotExist:
    db = cloud.create_database('WaterMgmt')
    
gdbs = [
    ('HUC2',"./import-data/wbdhu2_a_us_september2014.gdb"),
    ('HUC4',"./import-data/wbdhu4_a_us_september2014.gdb"),
    ('HUC6',"./import-data/wbdhu6_a_us_september2014.gdb"),
    #('HUC8',"./import-data/wbdhu8_a_us_september2014.gdb"),
    #('HUC10',"./import-data/wbdhu10_a_us_september2014.gdb"),
    #('HUC12',"./import-data/wbdhu12_a_us_september2014.gdb"),
]
    
for tname,fpath in gdbs:
    
    try:
        db.Table(tname).drop()
    except:
        pass
    
    data = ogr.Open(fpath)
    layer = data.GetLayer(0)
    spatialRef = layer.GetSpatialRef()
    layerDefinition = layer.GetLayerDefn()
    layerName = layer.GetName()
    firstFeat = next(layer)
    layerType =firstFeat.GetGeometryRef().GetGeometryName()
    print layerType
    print layer.GetFeatureCount()

    # You can't seem to easily reset the iterator and I couldn't access by index
    data = ogr.Open(fpath)
    layer = data.GetLayer(0)

    cols = []
    rows = []
    geomtype = set()
    srs = set()

    dtconv = {
        "String":"Text",
        "DateTime":"Text",
        "Integer":"Integer",
        "Real":"Float",
    }

    for i in range(layerDefinition.GetFieldCount()):
        #fieldWidth = layerDefinition.GetFieldDefn(i).GetWidth()
        #GetPrecision = layerDefinition.GetFieldDefn(i).GetPrecision()
        col = {
            "name":layerDefinition.GetFieldDefn(i).GetName(),
            "datatype":dtconv[layerDefinition.GetFieldDefn(i).GetFieldTypeName(
                        layerDefinition.GetFieldDefn(i).GetType())]
        }
        cols.append(col)
        
    cols += [{"name":"geom","datatype":"MultiPolygon"}]

    try:
        table = db.create_table(tname,cols)
    except cc.TableExists:
        db.Table(tname).drop()
        table = db.create_table(tname,cols)

    target = osr.SpatialReference()
    target.ImportFromEPSG(4326)

    transform = osr.CoordinateTransformation(spatialRef,target)

    for i,feature in enumerate(layer):
        geom = feature.GetGeometryRef()
        row = [feature.GetField(x['name']) for x in cols[:-1]]
        geom.Transform(transform)
        row.append(geom.ExportToWkt())
        table.insert(row)

    table.add_index(table.columns()[-1])
