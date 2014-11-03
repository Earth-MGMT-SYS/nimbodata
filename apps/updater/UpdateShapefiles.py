
import os
import subprocess
import StringIO
import zipfile
import tarfile
import gzip
import tempfile

import pycurl
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
            self._tables = [self.table_factory(self.single_table,fpath)]
            return self._tables
        else:
            return self.sources()
    
    def sources(self):
        try:
            return self._tables
        except AttributeError:
            pass
        
        retVal = []
        for fname,fpath in self.infiles:
            retVal.append(self.table_factory(fname,fpath))
        self._tables = retVal
        return retVal

class UpdateShapefileTable(object):
    """A table from a local Shapefile zip file."""
    
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
        try:
            p = subprocess.check_output(['shp2pgsql','-D','-a','-s 4326',self.fpath])
        except subprocess.CalledProcessError:
            p = subprocess.check_output(['shp2pgsql','-D','-a','-W "latin1"','-s 4326',self.fpath])
        f = StringIO.StringIO()
        for x in p.split('\n')[4:-3]:
            f.write(x+'\n')
        f.seek(0)
        return f


class UpdateShapefileZipURL(UpdateShapefileTable):
    """Adapter for a shapefile stored as a tar or zip at a url."""
    
    def __init__(self,name,url):
        print "Getting " + name + " ( " + url + " ) "
        tempdir = tempfile.mkdtemp()
        buf = StringIO.StringIO()
        curl = pycurl.Curl()
        curl.setopt(curl.URL, url)
        curl.setopt(curl.WRITEDATA, buf)
        curl.perform()
        curl.close()
        try:
            with zipfile.ZipFile(buf,'r') as myzip:
                myzip.extractall(tempdir)
        except:
            try:
                buf.seek(0)
                with tarfile.TarFile(fileobj=buf) as mytar:
                    mytar.extractall(tempdir)
            except:
                buf.seek(0)
                with tarfile.open(fileobj=buf,mode='r|gz') as mytar:
                    mytar.extractall(tempdir)
        
        fname = [ f for f in os.listdir(tempdir)
            if os.path.splitext(f)[1] == '.shp'][0]
                
        self.fname = fname
        self.fpath = os.path.join(tempdir,fname)
        self.name = name






