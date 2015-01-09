"""Module implements PostGIS datatypes in Nimbodata, also using shapely."""
# Copyright (C) 2014  Bradley Alan Smith

import json

import shapely.geometry as shp

from . import *


expressions.operators += [
    '~','@','=','&<','&<|','&>','|&>','<<','>>','<<|','|>>','<->'
]

class Geographic(Datatype):
    """Generic geographic type."""
    
    def from_literal(self,*args,**kwargs):
        return shp.asShape(json.loads(args[0]))
        
    # http://www.postgis.us/downloads/postgis21_cheatsheet.html
    ###########################################################################
    ##### POSTGIS OPERATOR FUNCTIONS ##########################################
    ###########################################################################
    def contains(self,this,other):
        return expressions.BinaryExpression(this['name'],'~',other)
        
    def containedby(self,this,other):
        return expressions.BinaryExpression(this['name'],'@',other)
        
    def same_bbox(self,this,other):
        return expressions.BinaryExpression(this['name'],'=',other)
        
    def overlap_or_left(self,this,other):
        return expressions.BinaryExpression(this['name'],'&<',other)
        
    def overlap_or_below(self,this,other):
        return expressions.BinaryExpression(this['name'],'&<|',other)
        
    def overlap_or_right(self,this,other):
        return expressions.BinaryExpression(this['name'],'&>',other)
        
    def overlap_or_above(self,this,other):
        return expressions.BinaryExpression(this['name'],'|&>',other)
        
    def leftof(self,this,other):
        return expressions.BinaryExpression(this['name'],'<<',other)
        
    def rightof(self,this,other):
        return expressions.BinaryExpression(this['name'],'>>',other)
        
    def below(self,this,other):
        return expressions.BinaryExpression(this['name'],'<<|',other)
    
    def above(self,this,other):
        return expressions.BinaryExpression(this['name'],'|>>',other)
    
    def distance_between(self,this,other):
        return expressions.BinaryExpression(this['name'],'<->',other)
        
    ###########################################################################
    ##### POSTGIS FUNCTIONS ###################################################
    ###########################################################################
    
    def intersects(self,this,other):
        return expressions.TwoValExpression('ST_Intersects',this['name'],other)

class Point(Geographic):
    """Simple X,Y point.  Extends PostGIS `POINT` and Shapely `Point`."""
    
    def from_literal(self,*args,**kwargs):
        """ Instantiate the Shapely Point """
        try:
            return shp.Point(*args,**kwargs)
        except TypeError as e:
            return Geographic.from_literal(self,*args,**kwargs)
            
class MultiPoint(Geographic):
    """Simple X,Y point.  Extends PostGIS `POINT` and Shapely `Point`."""
    
    def from_literal(self,*args,**kwargs):
        """ Instantiate the Shapely Point """
        try:
            return shp.MultiPoint(*args,**kwargs)
        except (TypeError,AssertionError) as e:
            return Geographic.from_literal(self,*args,**kwargs)

class Line(Geographic):
    """Line extends PostGIS `LINESTRING` and shapely `Linestring`."""
    
    def from_literal(self,*args,**kwargs):
        """ Instantiate the Shapely Point """
        try:
            return shp.LineString(*args,**kwargs)
        except Exception as e:
            return Geographic.from_literal(self,*args,**kwargs)


class MultiLine(Geographic):
    """MultiLine extends PostGIS `MULTILINESTRING` and shapely `MultiLineString`."""
    
    def from_literal(self,*args,**kwargs):
        """ Instantiate the Shapely Point """
        try:
            return shp.MultiLineString(*args,**kwargs)
        except Exception as e:
            return Geographic.from_literal(self,*args,**kwargs)   
    

class Polygon(Geographic):
    """MultiLine extends PostGIS `MULTILINESTRING` and shapely `MultiLineString`."""
    
    def from_literal(self,*args,**kwargs):
        """ Instantiate the Shapely Point """
        try:
            return shp.Polygon(*args,**kwargs)
        except Exception as e:
            return Geographic.from_literal(self,*args,**kwargs)   
            
            
class MultiPolygon(Geographic):
    """MultiLine extends PostGIS `MULTILINESTRING` and shapely `MultiLineString`."""
    
    def from_literal(self,*args,**kwargs):
        """ Instantiate the Shapely Point """
        try:
            return shp.MultiPolygon(*args,**kwargs)
        except Exception as e:
            return Geographic.from_literal(self,*args,**kwargs)   
