"""Module tests insert/update/delete functionality."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys
sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import Text,Integer

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient
    cloud = pyclient.connect("http://localhost:5000",cfg.user)

class TestInsert(unittest.TestCase):
    """Test inserts."""
    def setUp(self):
        """Create the database."""
        self.db = cloud.create_database('testdb')
    def tearDown(self):
        """Drop the database."""
        self.db.drop()
    
    #@unittest.skip('skip')
    def test_insert(self):
        """Can we insert simple datatypes?"""
        cols = [
                {'name':'pk','datatype':Text,'primary_key':True},
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Text},
                ]
        table = cloud.create_table(self.db,'testTable',cols)
        vals = ['george',3,'pigskin']
        rowid = table.insert(vals)
        self.assertTrue(rowid.startswith('row-'))
        values = [
                ('frank',2,'apple'),
                ('jerry',5,'orange'),
                ('ann',7,'fig'),
                ('francine',9,'tomato'),
                ]
        rowids = table.insert(values)
        self.assertEquals(len(rowids),4)
        for rowid in rowids:
            self.assertTrue(rowid.startswith('row-'))
    
    @unittest.skip('skip')
    def test_update(self):
        """Can we update a row?"""
        cols = [
                {'name':'pk','datatype':Text,'primary_key':True},
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Text},
                ]
        table = cloud.create_table(self.db,'testTable',cols)
        vals = ['george',3,'pigskin']
        rowids = cloud.insert(table,vals)
        values = [
                ('frank',2,'apple'),
                ('jerry',5,'orange'),
                ('ann',7,'fig'),
                ('francine',9,'tomato'),
                ]
        rowids = cloud.insert(table,values)
        cloud.update(table,rowids[0],{'pk':'peewee'})
        updated = cloud.getby_id(table,rowids[0])
        self.assertEquals(updated[0],'peewee')
    
    #@unittest.skip('skip')
    def test_insert_afterview(self):
        """Can we insert a row into a table after a view has been made?"""
        cols = [
                {'name':'pk','datatype':Text,'primary_key':True},
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Text},
                ]
        table = cloud.create_table(self.db,'testTable',cols)
        view = cloud.create_view(self.db,'testView',{'viewid':table})
        vals = ['george',3,'pigskin']
        rowid = table.insert(vals)
        self.assertTrue(rowid.startswith('row-'))
        values = [
                ('frank',2,'apple'),
                ('jerry',5,'orange'),
                ('ann',7,'fig'),
                ('francine',9,'tomato'),
                ]
        rowids = table.insert(values)
        self.assertEquals(len(rowids),4)
        for rowid in rowids:
            self.assertTrue(rowid.startswith('row-'))
    
        
        
def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestInsert))
    return suite

if __name__ == '__main__':
    unittest.main()
