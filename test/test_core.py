"""Module provides higher level system tests."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest,time,datetime
import sys

import config_cloud as cfg

sys.path.append('../')

from core.pg.datatypes import Text,Integer

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",cfg.user)

   

#@unittest.skip('skip')
class TestBasicDatabase(unittest.TestCase):
    """Tests the creation, population and destruction of a basic database."""
    cloud = cloud
    
    def setUp(self):
        args = ('Test',)
        self.db_args = args
        self.db = self.cloud.create_database(*args)
    
    def tearDown(self):
        """Drop the test database."""
        self.db.drop()

    def runTest(self):
        """Quick functional test."""
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
            {'name':'b','datatype':Text},
        ]
        
        table = self.db.create_table('testTable',cols)
        
        table = self.db.Table('testTable')
        
        values = [
            {'pk':'frank','a':2,'b':'apple'},
            {'pk':'jerry','a':5,'b':'orange'},
            {'pk':'ann','a':7,'b':'fig'},
            {'pk':'francine','a':9,'b':'tomato'},
        ]
        
        cols = table.columns()
        
        self.assertEquals(cols[0]['name'],'pk')
        
        pk = table.Column('pk')
        self.assertEquals(pk['name'],'pk')
        
        cols = [x['name'] for x in cols]
        self.assertEqual(cols,['pk','a','b'])
        table.insert(values)
        results = self.cloud.select(table)
        self.assertEqual(len(results),4)
        pks = [x['pk'] for x in results]
        avals = [x['a'] for x in results]
        bvals = [x['b'] for x in results]
        for x in ('frank','jerry','ann','francine'):
            self.assertIn(x,pks)
        for x in (2,5,7,9):
            self.assertIn(x, avals)
        for x in ('apple','orange','fig','tomato'):
            self.assertIn(x, bvals)
        table.drop()
        with self.assertRaises(cc.RelationDoesNotExist):
            view = self.cloud.select(table)

#@unittest.skip('skip')
class TestManyDatabases(unittest.TestCase):
    """Tests multiple databases."""
    def setUp(self):
        """
        Create a cloud store it to self.
        
        """        
        cols = [
            {'name':'pk','datatype':Text,'primary_key':True},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        values = [
            {'pk':'frank','a':2,'b':'apple'},
            {'pk':'jerry','a':5,'b':'orange'},
            {'pk':'ann','a':7,'b':'fig'},
            {'pk':'francine','a':9,'b':'tomato'},
        ]
        

        self.db1 = cloud.create_database('N1')
        self.db2 = cloud.create_database('N2')
        self.db3 = cloud.create_database('N3')
        self.db4 = cloud.create_database('N4')

        
    def tearDown(self):
        """
        Destroy the databases, close the cloud.
        
        """
        self.db1.drop()
        self.db2.drop()
        self.db3.drop()
        self.db4.drop()
    
    def test_basics(self):
        """Can we create many databases and tables and keep them straight?"""
        
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        values = [
            {'pk':'frank','a':2,'b':'apple'},
            {'pk':'jerry','a':5,'b':'orange'},
            {'pk':'ann','a':7,'b':'fig'},
            {'pk':'francine','a':9,'b':'tomato'},
        ]
        
        table1 = self.db1.create_table('tt1',cols)
        table2 = self.db1.create_table('tt2',cols)
        table1.insert(values)
        table2.insert(values)
        
        table3 = self.db2.create_table('tt3',cols)
        
        tables = cloud.Table().listing()
        self.assertEqual(len(tables),3)
        
        db1tables = self.db1.tables()
        self.assertEqual(len(db1tables),2)
        
        #db1tables = table1.listing()
        #self.assertEqual(len(db1tables),2)
        
        results = cloud.select(table1)
        self.assertEqual(len(results),4)
        results = cloud.select(table2)
        self.assertEqual(len(results),4)        
        dbs = cloud.Database().listing()
        self.assertEqual(len(dbs),4)
        dbnames = [x['name'] for x in dbs]
        self.assertIn('N1',dbnames)
        self.assertIn('N4',dbnames)
        self.assertEqual(len(dbnames),4)
        
    
def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestBasicDatabase))
    suite.addTest(getTests(TestManyDatabases))
    return suite

if __name__ == '__main__':
    unittest.main()
