"""Module tests geographic functionality."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys
from itertools import product

sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import Text,Point,Polygon,Float,Integer
from common.expressions import simplify

from common import tilecalc

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",cfg.user)

#@unittest.skip('skip')
class TestTile(unittest.TestCase):
    """Test the geographic functionality."""
    
    def setUp(self):
        """Create the database, table and insert some values."""
        try:
            self.db = cloud.create_database('geodb')
        except (cc.RelationExists,cc.IntegrityError):
            cloud.Database('geodb').drop()
            self.db = cloud.create_database('geodb')
        
        cols = [
            {'name':'state','datatype':Text},
            {'name':'geom','datatype':Point}
        ]
        
        self.table = cloud.create_table(self.db,'geotable',cols)
        home, poi = self.table.columns()
        self.table.add_index(poi)
        
        
        
        values = [
            ('Arizona',Point(-111,34)),
            ('California',Point(-120,37)),
            ('New Mexico',Point(-106,34)),
            ('Colorado',Point(-106,39)),
        ]
        
        try:
            self.rowids = self.table.insert(values)
        except TypeError as e:
            self.db.drop()
            raise e
        
        cols = [
            {'name':'state','datatype':Text},
            {'name':'geom','datatype':Polygon}
        ]
            
        self.table2 = cloud.create_table(self.db,'geo2',cols)
        
        values = [
            ('Arizona',Polygon([(-112,33),(-110,33),(-111,35)])),
            ('California',Polygon([(-121,36),(-119,36),(-120,37)])),
            ('New Mexico',Polygon([(-107,33),(-105,33),(-106,35)])),
            ('Colorado',Polygon([(-107,38),(-105,38),(-106,40)])),
        ]
        self.table2.insert(values)
                
        self.table.modify({
            'dobj':{
                'tilescheme':{
                    0:self.table,
                    1:self.table,
                    2:self.table2,
                    3:self.table2,
                    4:self.table2,
                    5:self.table2,
                    6:self.table2,
                    7:self.table2,
                    8:self.table2,
                    9:self.table2,
                    10:self.table2,
                    11:self.table2,
                    12:self.table2,
                    13:self.table2,
                    14:self.table2,
                    15:self.table2,
                    16:self.table2,
                    17:self.table2,
                    18:self.table2,
                }
            }
        })
    
    def tearDown(self):
        """Drop the database"""
        self.db.drop()
    
    #@unittest.skip('skip')
    def test_basics(self):
        """Can we get a feature tile, does it have the expected data?"""
        tile = self.table.tile(0,0,0)
        self.assertEqual(len(tile['features']),4)
        
        for z in range(4):
            for x,y in product(range(z**2),range(z**2)):
                tile = self.table.tile(x,y,z)                
                if len(tile['features']) > 0:
                    if z < 2:
                        self.assertEquals(tile['features'][0]['geometry']['type'],'Point')
                    else:
                        self.assertEquals(tile['features'][0]['geometry']['type'],'Polygon')
    
    #@unittest.skip('skip')    
    def test_simplify(self):
        """Can we get a simplified geometry?"""
        r = self.table2.select([simplify('geom',1)])


if __name__ == '__main__':
    unittest.main()
