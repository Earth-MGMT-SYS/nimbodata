"""Module provides higher level system tests."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest,time,datetime
import sys

import config_cloud as cfg

sys.path.append('../')

from core.pg.datatypes import *

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",cfg.user)


#@unittest.skip('skip')
class TestObjectDatabase(unittest.TestCase):
    """Tests the creation, population and destruction of a basic database."""
    cloud = cloud
    
    def setUp(self):
        args = ('Test',)
        self.db_args = args
        self.db = self.cloud.create_database(*args)
    
    def tearDown(self):
        """Drop the test database."""
        self.db.drop()

    def test_object(self):
        """Can we put data objects in and get them back out?  No PG 9.3"""
        db = cloud.get_byid(self.db.objid)
        self.assertEquals(db.info['name'],'Test')
        self.assertEquals(db.info['owner'],cfg.user)
        
        db = cloud.Database('Test')
        self.assertEquals(db.info['name'],'Test')
        self.assertEquals(db.info['owner'],cfg.user)
        
        with self.assertRaises(cc.RelationExists):
            self.cloud.create_database('Test')
        
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':DataObject},
        ]
        
        table = self.db.create_table('testTable',cols)
        
        table = self.db.Table('testTable')
        
        values = [
            {'pk':'frank','a':2,'b':{'j':1,'k':2}},
            {'pk':'jerry','a':5,'b':{'l':3,'m':4}},
            {'pk':'ann','a':7,'b':{'n':5,'o':6}},
            {'pk':'francine','a':9,'b':{'p':7,'q':8}},
        ]
        
        table.insert(values)
        results = self.cloud.select(table,order_by='a')
        
        self.assertEquals(results[0]['b']['j'],1)
        self.assertEquals(results[2]['b']['o'],6)
        
        pk, a, b = table.columns()
        
        where = b.contains({'k':2})
        results = self.cloud.select(table,where = where, order_by='a')
        self.assertEquals(len(results),1)
        
        where = b.containedby({'a':'charlie','k':2,'j':1})
        results = self.cloud.select(table,where = where, order_by='a')
        self.assertEquals(len(results),1)
        
        where = b.haskey('k')
        results = self.cloud.select(table,where = where, order_by='a')
        self.assertEquals(len(results),1)
        
        where = b.hasall(['n','o'])
        results = self.cloud.select(table,where = where, order_by='a')
        self.assertEquals(len(results),1)
        
        where = b.hasany(['k','m','o'])
        results = self.cloud.select(table,where = where, order_by='a')
        self.assertEquals(len(results),3)
        

    
def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestObjectDatabase))
    return suite

if __name__ == '__main__':
    unittest.main()
