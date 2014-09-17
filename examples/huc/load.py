import json

import ogr,osr,os,sys
from gdalconst import *

sys.path.append('../../core')
import cloud_controller as cc

cloud = cc.Cloud()

user = 'usr-67141db0-1c1d-4f51-9a8a-5a6a9f7917f7'
try:
    db = cloud.create_db('HUC',user)
except cc.RelationExists:
    cloud.drop_db(cloud.get_dbid('HUC',user))
    db = cloud.create_db('HUC',user)
    


data = ogr.Open("./data/WBDHU2_Mar2014.gdb")
layer = data.GetLayer(0)
spatialRef = layer.GetSpatialRef()
layerDefinition = layer.GetLayerDefn()
layerName = layer.GetName()
firstFeat = next(layer)
layerType =firstFeat.GetGeometryRef().GetGeometryName()
print layerType
print layer.GetFeatureCount()



# You can't seem to easily reset the iterator and I couldn't access by index
data = ogr.Open("./data/WBDHU2_Mar2014.gdb")
layer = data.GetLayer(0)

cols = []
rows = []
geomtype = set()
srs = set()

dtconv = {
    "String":"text",
    "DateTime":"text",
    "Integer":"integer",
    "Real":"float",
}

for i in range(layerDefinition.GetFieldCount()):
    
    #fieldWidth = layerDefinition.GetFieldDefn(i).GetWidth()
    #GetPrecision = layerDefinition.GetFieldDefn(i).GetPrecision()
    col = {
        "colname":layerDefinition.GetFieldDefn(i).GetName(),
        "dtype":dtconv[layerDefinition.GetFieldDefn(i).GetFieldTypeName(
                    layerDefinition.GetFieldDefn(i).GetType())]
    }
    cols.append(col)
    
cols += [{"colname":"boundary","dtype":"geography(MULTIPOLYGON,4326)"}]

try:
    table = cloud.create_table(db,'HUC2',user,cols)
except cc.TableExists:
    cloud.drop_table(cloud.get_tblid('HUC2',user))
    table = cloud.create_table(db,'HUC2',user,cols)

target = osr.SpatialReference()
target.ImportFromEPSG(4326)

transform = osr.CoordinateTransformation(spatialRef,target)

for i,feature in enumerate(layer):
    geom = feature.GetGeometryRef()
    row = [feature.GetField(x['colname']) for x in cols[:-1]]
    geom.Transform(transform)
    row.append(geom.ExportToWkt())
    cloud.insert(table,row)


