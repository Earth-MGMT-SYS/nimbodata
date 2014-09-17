"""Module tests the instantiation and effectiveness of PostgreSQL constraints."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest,time,datetime
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
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",cfg.user)

#@unittest.skip('skip')
class TestConstraints(unittest.TestCase):
    """Test column restraint creation and enforcement."""
    
    def setUp(self):
        """Create the database, table and columns."""
        try:
            self.db = cloud.create_database('constraints')
        except:
            cloud.Database('constraints').drop()
            self.db = cloud.create_database('constraints')
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text}
            ]
        self.table = self.db.create_table('mod',cols)
    
    def tearDown(self):
        """Drop the database."""
        self.db.drop()
    
    #@unittest.skip('skip')
    def test_check_str(self):
        """Can we do a check constraint with text datatype?"""
        constraint = {
            'tblid':self.table,
            'conname':'testconst',
            'contype':'check',
            'col':'pk',
            'op':'!=',
            'compval':'francine'
        }
        constraint = cloud.create_constraint(constraint)
        values = [
            {'pk':'frank','a':2,'b':'apple'},
            {'pk':'jerry','a':5,'b':'orange'},
            {'pk':'ann','a':7,'b':'fig'},
            {'pk':'francine','a':9,'b':'tomato'}
        ]
        with self.assertRaises(cc.IntegrityError):
            self.table.insert(values)
        constraint.drop()
        values = [
            {'pk':'francine','a':9,'b':'tomato'}
        ]
        self.table.insert(values)
    
    #@unittest.skip('skip')
    def test_check_int(self):
        """Can we do a check constraint with an integer datatype?"""
        constraint = {
            'tblid':self.table,
            'conname':'testconst',
            'contype':'check',
            'col':'a',
            'op':'<',
            'compval':9
        }
        constraint = cloud.create_constraint(constraint)
        values = [
            {'pk':'frank','a':2,'b':'apple'},
            {'pk':'jerry','a':5,'b':'orange'},
            {'pk':'ann','a':7,'b':'fig'},
            {'pk':'francine','a':9,'b':'tomato'}
        ]
        with self.assertRaises(cc.IntegrityError):
            result = self.table.insert(values)
        constraint.drop()
        values = [
            {'pk':'francine','a':9,'b':'tomato'}
        ]
        self.table.insert(values)
    
    #@unittest.skip('skip')
    def test_check_notnull(self):
        """Can we do a not null constraint?"""
        constraint = {
            'tblid':self.table,
            'conname':'testconst',
            'contype':'notnull',
            'col':'a'
        }
        constraint = cloud.create_constraint(constraint)
        values = [
            {'pk':'frank','a':2,'b':'apple'},
            {'pk':'jerry','a':5,'b':'orange'},
            {'pk':'ann','a':7,'b':'fig'},
            {'pk':'francine','b':'tomato'}
        ]
        with self.assertRaises(cc.IntegrityError):
            result = self.table.insert(values)
        constraint.drop()
        values = [
            {'pk':'francine','b':'tomato'}
        ]
        self.table.insert(values)
            
    #@unittest.skip('skip')
    def test_check_unique(self):
        """Can we do a unique constraint?"""
        constraint = {
            'tblid':self.table,
            'conname':'testconst',
            'contype':'unique',
            'col':'a'
        }
        constraint = cloud.create_constraint(constraint)
        values = [
            {'pk':'frank','a':2,'b':'apple'},
            {'pk':'jerry','a':5,'b':'orange'},
            {'pk':'ann','a':7,'b':'fig'},
            {'pk':'ann','a':7,'b':'fig'},
        ]
        with self.assertRaises(cc.IntegrityError):
            result = self.table.insert(values)
        constraint.drop()
        values = [
            {'pk':'ann','a':7,'b':'fig'},
        ]
        self.table.insert(values)
        

def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestConstraints))
    return suite

if __name__ == '__main__':
    unittest.main()
