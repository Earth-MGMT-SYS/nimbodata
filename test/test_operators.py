"""Module tests query functionality (select)."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys
import datetime
sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import *
from common.expressions import *

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient
    cloud = pyclient.connect("http://localhost:5000",cfg.user)

class TestFunctions(unittest.TestCase):
    """Test the functionality of the Select module."""
    def setUp(self):
        """Create the database, a table and insert some values."""
        try:
            self.db = cloud.create_database('selectdb')
        except cc.IntegrityError:
            cloud.Database('selectdb').drop()
            self.db = cloud.create_database('selectdb')
    
    def _intvals(self):
        cols = [
            {'name':'pk','datatype':Text,'primary_key':True},
            {'name':'a','datatype':Integer,'alias':'Boffo'},
            {'name':'b','datatype':Integer,'alias':'Ricardo'},
            {'name':'c','datatype':Integer},
            {'name':'d','datatype':Integer},
            {'name':'e','datatype':Integer},
        ]
        
        self.table = cloud.create_table(self.db,'testTable',cols)
        self.values = [
            ('a',2,4,6,8,4),
            ('b',5,10,15,50,25),
            ('c',7,14,21,98,49),
            ('d',9,18,27,162,81),
        ]
        
        self.rowids = self.table.insert(self.values)
        
    def tearDown(self):
        """Drop the database."""
        self.db.drop()
    
    #@unittest.skip('skip')
    def test_arithmetic(self):
        """Can we do a group by with an aggregate function?"""
        self._intvals()
        pk, a, b, c, d, e  = self.table.columns()
        
        cols = [a + b, c]
        results = self.table.select(
            cols=cols
        )
        
        self.assertEquals(results.header[0]['alias'],'Boffo + Ricardo')
        self.assertEquals(results.header[0]['name'],'a + b')
        
        for row in results:
            self.assertEquals(row[0],row[1])
        
        cols = [a * b, d]
        results = self.table.select(
            cols=cols
        )
        
        for row in results:
            self.assertEquals(row[0],row[1])
            
        cols = [b / 2, a]
        results = self.table.select(
            cols=cols
        )
        
        for row in results:
            self.assertEquals(row[0],row[1])
            
        cols = [a ** 2, e]
        results = self.table.select(
            cols=cols
        )
        
        for row in results:
            self.assertEquals(row[0],row[1])
        
        '''
        cols = [b % 2]
        results = self.table.select(
            cols=cols
        )
        
        for row in results:
            self.assertEquals(row[0],0)
        '''


if __name__ == '__main__':
    unittest.main()
