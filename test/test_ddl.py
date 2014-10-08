"""Module tests the instantiation of database entities."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys

from shapely.geometry import *
import psycopg2

sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import Text,Integer, Float

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",cfg.user)

class TestDDL(unittest.TestCase):
    """Test the SQL DDL functionality."""
    def setUp(self):
        """Instantiate a db, drop and instantiate if the first try fails."""
        try:
            self.db = cloud.create_database('selectdb')
        except cc.RelationExists:
            db = cloud.Database('selectdb').drop()
            self.db = cloud.create_database('selectdb')
    def tearDown(self):
        """Drop the database."""
        try:
            self.db.drop()
        except (psycopg2.ProgrammingError,cc.RelationDoesNotExist):
            # One of the tests drops the DB, this will fail on that test.
            pass

    #@unittest.skip('skip')
    def test_db_and_table(self):
        """Can we create a simple database with a single simple table?"""
        cols = [
            {'name':'pk','datatype':Text,'primary_key':True},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        self.table = self.db.create_table('testTable',cols)
        pk,a,b = self.table.columns()
        self.table.add_index(pk,True)
        self.table.add_index(b)
        
        values = [
            ('frank',2,'apple'),
            ('jerry',5,'orange'),
            ('ann',7,'fig'),
            ('francine',9,'tomato'),
        ]
        
        dbs = cloud.Database().listing()
        # Ensure that there's one and only one result
        self.assertEquals(len(dbs),1)
        self.assertEquals(self.table.info['name'],'testTable')
        
        self.table.modify({'name':'KingKong','alias':'Flappy'})
        self.assertEquals(self.table.info['name'],'KingKong')
        self.assertEquals(self.table.info['alias'],'Flappy')
        
        self.db.modify({'name':'BozoHappyland','alias':'FrankrankBoffinBrew'})
        self.assertEquals(self.db.info['name'],'BozoHappyland')
        self.assertEquals(self.db.info['alias'],'FrankrankBoffinBrew')
        
    #@unittest.skip('skip')
    def test_cols(self):
        """Can we create and modify columns?"""
        cols = [
            {'name':'pk','alias':'P K','datatype':Text},
            {'name':'a','alias':'A col','datatype':Integer},
            {'name':'b','alias':'b COL','datatype':Text},
        ]
        self.table = self.db.create_table('Colstuff',cols)
        pk, a, b = self.table.columns()
        self.assertEqual(pk['name'],'pk')
        values = [
            ('frank',2,'1'),
            ('jerry',5,'2'),
            ('ann',7,'3'),
            ('francine',9,'4'),
        ]
        self.table.insert(values)
        vals = cloud.select(self.table)
        self.assertEquals(vals[0]['b'],'1')
        self.assertEquals(vals[0]['a'],2)
        cols = self.table.columns()
        self.assertEquals(cols[0]['alias'],'P K')
        b.modify({'datatype':'Integer'})
        vals = cloud.select(self.table)
        self.assertEquals(vals[0]['b'],1)
        # If the user says go... go.  It is hard to be safe and reliable too.
        #with self.assertRaises(cc.DataError):
        #    pk.modify('Float')
        pk, a, b = self.table.columns()
        self.assertEquals(pk['datatype'],'Text')
        
    #@unittest.skip('skip')
    def test_add_column_as(self):
        """Can we add a column as an expression on another?"""
        
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
            {'name':'c','datatype':Text},
        ]
        self.table = self.db.create_table('Colstuff',cols)
        pk, a, b, c = self.table.columns()
        values = [
            ('frank',2,'1','1.1'),
            ('jerry',5,'2','2.2'),
            ('ann',7,'3','3.3'),
            ('francine',9,'4','4.4'),
        ]
        self.table.insert(values)
        vals = cloud.select(self.table)
        self.assertEquals(vals[0]['b'],'1')
        
        self.table.add_columns([
            {'name':'d','datatype':'Integer','exp':Integer(b)},
            {'name':'e','datatype':'Text','exp':Text(a)},
            {'name':'f','datatype':'Float','exp':Float(c)}
        ])
        
        vals = cloud.select(self.table)
        
        self.assertEquals(vals[0]['d'],1)
        self.assertEquals(vals[0]['e'],'2')
        self.assertEquals(vals[0]['f'],1.1)
        
    #@unittest.skip('skip')
    def test_addRow(self):
        """Ensure that we can insert into a newly created table."""
        cols = [
                {'name':'pk','datatype':Text},
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Text},
        ]
        self.table = self.db.create_table('testTable',cols)
        cols = self.table.columns()
        indicies = [x['weight'] for x in cols]
        col = [{'name':'c','datatype':Text}]
        self.table.add_columns(col)
        cols = self.table.columns()
        indicies = [x['weight'] for x in cols]
        self.assertEquals(indicies[-1],3)
        dbs = cloud.Database().listing()
        # Ensure that there's one and only one result
        self.assertEquals(len(dbs),1)
    
    #@unittest.skip('skip')
    def test_drop_table(self):
        """Can we drop a table?"""
        table = self.db.create_table('testme',[])
        tblid = table['objid']
        table.drop()
        table_objids = [x['objid'] for x in self.db.tables()]
        self.assertNotIn(tblid,table_objids)
        
    #@unittest.skip('skip')
    def test_drop_table_with_children(self):
        """Can we drop a table with children (i.e. columns)?"""
        cols = [
                {'name':'pk','datatype':Text},
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Text},
        ]
        table = self.db.create_table('testTable',cols)
        table_cols = [x['objid'] for x in table.columns()]
        col_list = [x['objid'] for x in cloud.Column().listing()]
        self.assertIn(table_cols[0],col_list)
        table.drop()
        col_list = [x['objid'] for x in cloud.Column().listing()]
        self.assertNotIn(table_cols[0],col_list)
    
    #@unittest.skip('skip')
    def test_drop_db_with_grandchildren(self):
        """Can we drop a database with grandchildren (i.e. columns)?"""
        cols = [
                {'name':'pk','datatype':Text},
                {'name':'a','datatype':Integer},
                {'name':'b','datatype':Text},
        ]
        table = self.db.create_table('testTable',cols)
        table_cols = [x['objid'] for x in table.columns()]
        col_list = [x['objid'] for x in cloud.Column().listing()]
        self.assertIn(table_cols[0],col_list)
        self.db.drop()
        col_list = [x['objid'] for x in cloud.Column().listing()]
        self.assertNotIn(table_cols[0],col_list)
        
    #@unittest.skip('skip')
    def test_drop_column(self):
        """Can we drop a column?"""
        cols = [
            {'name':'a','datatype':Text},
            {'name':'b','datatype':Text}
        ]
        self.table = self.db.create_table('testTable',cols)
        cols = self.table.columns()
        self.assertEquals(cols[0]['name'],'a')
        cloud.Column(objid=cols[0]['objid']).drop()
        cols = self.table.columns()
        self.assertEquals(cols[0]['name'],'b')
    
    #@unittest.skip('skip')
    def test_rename_column(self):
        """Can we can rename a column?"""
        cols = [
            {'name':'a','datatype':Text},
            {'name':'b','datatype':Text}
        ]
        self.table = self.db.create_table('testTable',cols)
        got_cols = self.table.columns()
        num_cols = len(got_cols)
        cloud.Column(objid=got_cols[0]['objid']).rename('G')
        self.assertEquals(num_cols,len(self.table.columns()))
        self.assertEquals(self.table.columns()[0]['name'],'G')
    
    #@unittest.skip('skip')
    def test_rename_table(self):
        """Can we can rename a table?"""
        self.table = self.db.create_table('testTable',[])
        self.assertEquals(self.table.info['name'],'testTable')
        self.table.rename('borfo')
        self.assertEquals(self.table.info['name'],'borfo')
    
    #@unittest.skip('skip')
    def test_rename_db(self):
        """Can we rename a database?"""
        dbs = cloud.Database().listing()
        self.assertEquals(len(dbs),1)
        self.assertEquals(dbs[0]['name'],'selectdb')
        cloud.Database(objid=dbs[0]['objid']).rename('barf')
        dbs = cloud.Database().listing()
        self.assertEquals(len(dbs),1)
        self.assertEquals(dbs[0]['name'],'barf')        


def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestDDL))
    return suite

if __name__ == '__main__':
    unittest.main()
