"""Module registers custom datatypes with psycopg2."""
# Copyright (C) 2014  Bradley Alan Smith

import psycogreen.gevent
import psycopg2
import psycopg2.extras
import shapely.geometry as shp

from . import *
import common.datatypes.ranges as base_range

#psycogreen.gevent.patch_psycopg()

_RANGE = psycopg2.extensions.new_type((3904,), "INT4RANGE", IntegerRange)
psycopg2.extensions.register_type(_RANGE)

psycopg2.extensions.register_adapter(base_range.IntegerRange,RangeAdapter)


psycopg2.extras.register_json(oid=3802, array_oid=3807, globally=True)

psycopg2.extensions.register_adapter(shp.Point,GeoAdapter)
psycopg2.extensions.register_adapter(shp.MultiPoint,GeoAdapter)
psycopg2.extensions.register_adapter(shp.LineString,GeoAdapter)
psycopg2.extensions.register_adapter(shp.MultiLineString,GeoAdapter)
psycopg2.extensions.register_adapter(shp.Polygon,GeoAdapter)
psycopg2.extensions.register_adapter(shp.MultiPolygon,GeoAdapter)



PointCaster = psycopg2.extensions.new_type((18918,), "Point", GeoAdapter.cast)
psycopg2.extensions.register_type(PointCaster)

LineCaster = psycopg2.extensions.new_type((17466,), "Line", GeoAdapter.cast)
psycopg2.extensions.register_type(LineCaster)

psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
