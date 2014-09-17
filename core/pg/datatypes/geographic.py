"""Module implements PostGIS datatypes in Nimbodata, also using shapely."""
# Copyright (C) 2014  Bradley Alan Smith

import shapely.geometry as shp

from . import *
from . import PG_Datatype as Datatype
import common.datatypes.geographic as geo
from common import comparable

class Geographic(Datatype):
    """Generic geographic type."""
        
    def sql_target(self,colid,colname,alias=True,viewcreate=False):
        """ Return the column results as GeoJSON string"""
        if viewcreate:
            return ''' "%(colid)s" ''' % { 'colid':colid }
        elif alias:
            return ''' ST_AsGeoJSON("%(colid)s") AS "%(colname)s" ''' % {
                'colid':colid,
                'colname':colname
            }
        else:
            return ''' ST_AsGeoJSON("%(colid)s") AS "%(colid)s" ''' % {
                'colid':colid
            }    

class Point(geo.Point,Geographic):
    """Simple X,Y point.  Extends PostGIS `POINT` and Shapely `Point`."""
        
    def sql_create(self):
        return 'geometry(POINT,4326)'


class MultiPoint(geo.MultiPoint,Geographic):
    """Simple X,Y point.  Extends PostGIS `POINT` and Shapely `Point`."""
        
    def sql_create(self):
        return 'geometry(MULTIPOINT,4326)'


class Line(geo.Line,Geographic):
    """Linestring extends PostGIS `LINESTRING` and shapely `Linestring`."""
        
    def sql_create(self):
        return 'geometry(LINESTRING,4326)'

        
class MultiLine(geo.MultiLine,Geographic):
    
    def sql_create(self):
        return 'geometry(MULTILINESTRING,4326)'

        
class Polygon(geo.Polygon,Geographic):
    
    def sql_create(self):
        return 'geometry(POLYGON,4326)'


class MultiPolygon(geo.MultiPolygon,Geographic):
    
    def sql_create(self):
        return 'geometry(MULTIPOLYGON,4326)'


class GeoAdapter(object):
    """Adapt shapely.geography for psycopg2."""
    
    def __init__(self,f):
        self._f = f
    
    def getquoted(self):
        return "'SRID=4326;%s'" % self._f.wkt

    
    @staticmethod
    def cast(s, cur):
        if s is None:
            return None
        else:
            return s


