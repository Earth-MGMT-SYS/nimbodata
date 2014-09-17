
import os
import subprocess
import StringIO
import zipfile
import osgeo.ogr

from core.pg.datatypes import *

type_map = {
    'multipolygon':MultiPolygon,
    'polygon':Polygon,
    'point':Point,
    'multipoint':MultiPoint,
    'linestring':Line,
    'multilinestring':MultiLine,
}

class UpdateShapefileDatabase(object):
    """A database drawn from CSV files."""
    
    def __init__(self,name,infiles,table_factory,single_table=False):
        self.name, self.infiles, self.table_factory = name, infiles, table_factory
        self.single_table = single_table
    
    def tables(self):
        if self.single_table:
            fname,fpath = self.infiles[0]
            return [self.table_factory(self.single_table,fpath)]
        
        retVal = []
        for fname,fpath in self.infiles:
            retVal.append(self.table_factory(fname,fpath))
        return retVal
        
    def sources(self):
        retVal = []
        for fname,fpath in self.infiles:
            retVal.append(self.table_factory(fname,fpath))
        return retVal

class UpdateShapefileTable(object):
    """A table from a Shapefile zip file."""
    
    def __init__(self,fname,fpath):
        if os.path.splitext(fpath)[1] == '.zip':
            with zipfile.ZipFile(fpath,'r') as myzip:
                myzip.extractall('./import-data/zips')
            fpath = os.path.splitext(fpath)[0] + '.shp'
        self.fname, self.fpath = fname, fpath
        self.name = os.path.splitext(fname)[0]
        
        
    @property
    def columns(self):
        p = subprocess.check_output(['shp2pgsql','-p',self.fpath])
        linebegin = 'SELECT AddGeometryColumn('
        geoline = filter(lambda x: x.startswith(linebegin),p.split('\n'))[0]
        geoline = geoline.split('(')[1][:-2]
        parts = geoline.rsplit(',',2)[1:]
        geotype = type_map[parts[0].replace("'",'').lower()]
        
        shp = osgeo.ogr.Open(self.fpath)
        layer = shp.GetLayer()
        lyrdef = layer.GetLayerDefn()
        cols = []
        for i in range(lyrdef.GetFieldCount()):
            fieldName =  lyrdef.GetFieldDefn(i).GetName()
            fieldTypeCode = lyrdef.GetFieldDefn(i).GetType()
            fieldType = lyrdef.GetFieldDefn(i).GetFieldTypeName(fieldTypeCode)
            cols.append({'name':fieldName,'datatype':Text})
        cols.append({'name':'geom','datatype':geotype})
        return cols
        
    def asfile(self):
        p = subprocess.check_output(['shp2pgsql','-D','-a','-s 4326',self.fpath])
        f = StringIO.StringIO()
        for x in p.split('\n')[4:-3]:
            f.write(x+'\n')
        f.seek(0)
        return f