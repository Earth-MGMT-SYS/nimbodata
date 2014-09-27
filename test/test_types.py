"""Module tests PostgreSQL types."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest,time,datetime
import sys
import json
sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import *

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient
    cloud = pyclient.connect("http://localhost:5000",cfg.user)


#@unittest.skip('skip')
class TestTypes(unittest.TestCase):
    """Test type and column functionality."""
    
    def __init__(self,x):
        self.cloud = cloud
        unittest.TestCase.__init__(self,x)
    
    def setUp(self):
        args = ('columns',)
        try:
            self.db = self.cloud.create_database(*args)
        except:
            self.cloud.Database(*args).drop()
            self.db = self.cloud.create_database(*args)
    
    def tearDown(self):
        self.db.drop()
    
    #@unittest.skip('skip')
    def test_string(self):
        """Do strings work?"""
        cols = [
                {'name':'a','datatype':Text},
                {'name':'b','datatype':Text}
               ]
        rows = [('pie','apple'),('custard','vanilla')]
        table = self.cloud.create_table(self.db,'stringtable',cols)
        table.insert(rows)
        vals = self.cloud.select(table,order_by='a')
        self.assertEqual(vals[0][0],'custard')
        self.assertEqual(vals[1][0],'pie')
        self.assertEqual(vals[0][1],'vanilla')
        self.assertEqual(vals[1][1],'apple')
    
    #@unittest.skip('skip')
    def test_integer(self):
        """Do integers work?"""
        cols = [
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Integer}
               ]
        rows = [(1,2),(3,4)]
        table = self.cloud.create_table(self.db,'inttable',cols)
        table.insert(rows)
        vals = self.cloud.select(table,order_by='a')
        self.assertEqual(vals[0][0],1)        
        self.assertEqual(vals[0][1],2)        
        self.assertEqual(vals[1][0],3)        
        self.assertEqual(vals[1][1],4)
        
    #@unittest.skip('skip')
    def test_range(self):
        """Do integer ranges work?"""
        cols = [
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':IntegerRange}
        ]
        rows = [
            (0,IntegerRange('[0,100]')), # String casting in Psycopg2...
            (1,'[0,100)'),
            (2,'(0,100)'),
            (3,'(0,100]')
        ]
        table = self.cloud.create_table(self.db,'rangetable',cols)
        table.insert(rows)
        vals = self.cloud.select(table,order_by='a')
        self.assertTrue(0 in vals[0][1])
        self.assertTrue(100 in vals[0][1])
        
        self.assertTrue(0 in vals[0][1])
        self.assertTrue(100 not in vals[1][1])
        
        self.assertTrue(0 not in vals[2][1])
        self.assertTrue(100 not in vals[2][1])
        
        self.assertTrue(0 not in vals[3][1])
        self.assertTrue(100 in vals[3][1])
    
    #@unittest.skip('skip')
    def test_float(self):
        """Do floats work?"""
        cols = [
                {'name':'a','datatype':Float},
                {'name':'b','datatype':Float}
               ]
        rows = [(1.1,2.2),(3.3,4.4)]
        table = self.cloud.create_table(self.db,'floattable',cols)
        table.insert(rows)
        vals = self.cloud.select(table,order_by='a')
        self.assertEqual(vals[0][0],1.1)        
        self.assertEqual(vals[0][1],2.2)        
        self.assertEqual(vals[1][0],3.3)        
        self.assertEqual(vals[1][1],4.4)
    
    #@unittest.skip('skip')
    def test_bool(self):
        """Do booleans work?"""
        cols = [
                {'name':'a','datatype':Text},
                {'name':'b','datatype':Boolean}
               ]
        rows = [('fred',True),('alice',False),('betty',False),('george',True)]
        table = self.cloud.create_table(self.db,'booleantable',cols)
        table.insert(rows)
        view = self.cloud.select(table,order_by='a')
        self.assertEqual(view[0][1],False)        
        self.assertEqual(view[1][1],False)        
        self.assertEqual(view[2][1],True)
        self.assertEqual(view[3][1],True)
    
    #@unittest.skip('skip')
    def test_date(self):
        """Do dates work?"""
        cols = [
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Date}
               ]
        rows = [(2,datetime.date(1911,1,1)),(1,datetime.date(1950,1,1))]
        table = self.cloud.create_table(self.db,'datetable',cols)
        table.insert(rows)
        view = self.cloud.select(table,order_by='a')
        self.assertEqual(view[0][1],datetime.date(1950,1,1))
        self.assertEqual(view[1][1],datetime.date(1911,1,1))
    
    #@unittest.skip('skip')
    def test_timestamp(self):
        """Do timestamps work?"""
        cols = [
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Timestamp}
               ]
        rows = [(2,Timestamp(1911,1,1,1,1)),
                (1,Timestamp(1950,1,1,1,1))]
        table = self.cloud.create_table(self.db,'datetable',cols)
        table.insert(rows)
        view = self.cloud.select(table,order_by='a')
        self.assertEqual(view[0][1],datetime.datetime(1950,1,1,1,1))
        self.assertEqual(view[1][1],datetime.datetime(1911,1,1,1,1))
    
    #@unittest.skip('skip')
    def test_time(self):
        """Do times work?"""
        cols = [
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Time}
               ]
        rows = [(2,datetime.time(1,1,5)),
                (1,datetime.time(1,1,20))]
        table = self.cloud.create_table(self.db,'datetable',cols)
        table.insert(rows)
        view = self.cloud.select(table,order_by='a')
        self.assertEqual(view[0][1],datetime.time(1,1,20))
        self.assertEqual(view[1][1],datetime.time(1,1,5))
    
    #@unittest.skip('skip')
    def test_json(self):
        """Does stringy JSON work?"""
        cols = [
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Json}
               ]
        rows = [(2,json.dumps({'hello':'waffo'})),
                (1,json.dumps({'hello':'gorgo'}))]
        table = self.cloud.create_table(self.db,'datetable',cols)
        table.insert(rows)
        view = self.cloud.select(table,order_by='a')
        self.assertEqual(view[0][1],{u'hello':u'gorgo'})
        self.assertEqual(view[1][1],{u'hello':u'waffo'})        
    
    #@unittest.skip('skip')
    def test_jsonb(self):
        """Does binary JSON work?  Will not pass PG 9.3."""
        cols = [
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':DataObject}
               ]
        rows = [(2,{'hello':'waffo'}),
                (1,{'hello':'gorgo'})]
        table = self.cloud.create_table(self.db,'datetable',cols)
        table.insert(rows)
        view = self.cloud.select(table,order_by='a')
        self.assertEqual(view[0]['b'],{u'hello':u'gorgo'})
        self.assertEqual(view[1]['b'],{u'hello':u'waffo'})    
    
    #@unittest.skip('skip')
    def test_geog_point(self):
        """Does a geographic point work?"""
        cols = [
            {'name':'home','datatype':Text},
            {'name':'poi','datatype':Point}
        ]
        table = self.cloud.create_table(self.db,'geotable',cols)
        values = [
                ('frank',Point(-110,30)),
                ('jerry',Point(-110,30)),
                ('ann',Point(-110,30)),
                ('francine',Point(-110,30)),
                ]
        table.insert(values)
        results = self.cloud.select(table)
        self.assertEquals(results[0][1].x,-110)
        table.drop()
        
    #@unittest.skip('skip')
    def test_geog_multipoint(self):
        """Does a geographic multipoint work?"""
        cols = [
            {'name':'home','datatype':Text},
            {'name':'poi','datatype':MultiPoint}
        ]
        table = cloud.create_table(self.db,'geotable',cols)
        gj = """
            { "type": "MultiPoint",
                "coordinates": [ [100.0, 0.0], [101.0, 1.0] ]
                }
        """
        values = [
            ('jerry',MultiPoint(gj))
        ]
        table.insert(values)
        view = self.cloud.select(table)
        self.assertEquals(view[0][1].bounds,(100.0, 0.0, 101.0, 1.0))
        table.drop()
    
    #@unittest.skip('skip')
    def test_geog_line(self):
        """Does a geographic line work?"""
        cols = [
            {'name':'home','datatype':Text},
            {'name':'poi','datatype':Line}
        ]
        table = cloud.create_table(self.db,'geotable',cols)
        A, B = Point(-110,30), Point(-100,20)
        values = [
            ('frank',Line(((-110,30),(-100,20)))),
            ('jerry',Line((A,B)))
        ]
        table.insert(values)
        view = self.cloud.select(table)
        self.assertEquals(view[0][1].bounds,(-110.0,20.0,-100.0,30.0))
        self.assertEquals(round(view[0][1].length,0),14)
        table.drop()
        
    #@unittest.skip('skip')
    def test_geog_multiline(self):
        """Does a geographic multiline work?"""
        cols = [
            {'name':'home','datatype':Text},
            {'name':'poi','datatype':MultiLine}
        ]
        table = cloud.create_table(self.db,'geotable',cols)
        gj = """
        {   
            "type": "MultiLineString",
            "coordinates": [
                [ [100.0, 0.0], [101.0, 1.0] ],
                [ [102.0, 2.0], [103.0, 3.0] ]
              ]
        }
        """
        values = [
            ('jerry',MultiLine(gj))
        ]
        table.insert(values)
        view = self.cloud.select(table)
        self.assertEquals(view[0][1].bounds,(100.0, 0.0, 103.0, 3.0))
        self.assertEquals(round(view[0][1].length,0),3)
        table.drop()
    
    #@unittest.skip('skip')
    def test_geog_polygon(self):
        """Does a geographic polygon work?"""
        cols = [
            {'name':'home','datatype':Text},
            {'name':'poi','datatype':Polygon}
        ]
        table = cloud.create_table(self.db,'geotable',cols)
        gj = """
            { "type": "Polygon",
                "coordinates": [
                  [ [100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0] ]
                  ]
               }
        """
        values = [
            ('jerry',Polygon(gj))
        ]
        table.insert(values)
        view = self.cloud.select(table)
        self.assertEquals(view[0][1].bounds,(100.0, 0.0, 101.0, 1.0))
        self.assertEquals(round(view[0][1].area,0),1)
        table.drop()
        
    #@unittest.skip('skip')
    def test_geog_multipolygon(self):
        """Does a geographic multipolygon work?"""
        cols = [
            {'name':'home','datatype':Text},
            {'name':'poi','datatype':MultiPolygon}
        ]
        table = cloud.create_table(self.db,'geotable',cols)
        gj = """
            { "type": "MultiPolygon",
                "coordinates": [
                  [[[102.0, 2.0], [103.0, 2.0], [103.0, 3.0], [102.0, 3.0], [102.0, 2.0]]],
                  [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]],
                   [[100.2, 0.2], [100.8, 0.2], [100.8, 0.8], [100.2, 0.8], [100.2, 0.2]]]
                  ]
                }
        """
        values = [
            ('jerry',MultiPolygon(gj))
        ]
        table.insert(values)
        view = self.cloud.select(table)
        self.assertEquals(view[0][1].bounds,(100.0, 0.0, 103.0, 3.0))
        self.assertEquals(round(view[0][1].area,0),2)
        table.drop()
        
        
def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestTypes))
    return suite

if __name__ == '__main__':
    unittest.main()
