"""Module provides higher level system tests."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest,time,datetime
import sys

import config_cloud as cfg

sys.path.append('../')

from core.pg.datatypes import Text,Integer
import common.api as api

target = 'local'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",cfg.user)

#@unittest.skip('skip')
class TestAuth(unittest.TestCase):
    
    def setUp(self):
        """Instantiate a db, drop and instantiate if the first try fails."""
        try:
            self.db = cloud.create_database('selectdb')
        except cc.IntegrityError:
            db = cloud.Database('selectdb').drop()
            self.db = cloud.create_database('selectdb')
    def tearDown(self):
        """Drop the database."""
        
        if target == 'rest':
            cloud = cc.connect("http://localhost:5000",cfg.user)
        elif target == 'local':
            cloud = cc.Cloud(cfg.user)
        
        cloud.Database(self.db).drop()
    
    def test_not_allowed(self):
        """Does the auth module prevent access in the correct circumstances?"""
        self.db.rename('fancy')
        
        table = self.db.create_table('owner',[{'name':'boffo','datatype':Text}])
        table2 = self.db.create_table('gungy',[{'name':'boffo','datatype':Text}])
        view = self.db.create_view('stinky',{'viewid':table})
        
        table.rename('frango')
        view.rename('spangy')
        col = self.db.Column(table2.columns()[0])
        col.modify({'datatype':'Float'})
        
        if target == 'rest':
            bad_cloud = cc.connect("http://localhost:5000",cfg.b)
        elif target == 'local':
            bad_cloud = cc.Cloud(cfg.b)
        
        bad_db = bad_cloud.Database(self.db)
        with self.assertRaises(cc.NotAuthorized):
            bad_db.rename('gorgo')
            
        with self.assertRaises(cc.NotAuthorized):
            bad_db.create_table('gorgo',[])
            
        with self.assertRaises(cc.NotAuthorized):
            bad_db.drop()
        
        bad_table = bad_cloud.Table(table)
        with self.assertRaises(cc.NotAuthorized):
            bad_table.rename('boofkins')
            
        with self.assertRaises(cc.NotAuthorized):
            bad_table.add_columns([{'name':'boofkins','datatype':'Text'}])
        
        with self.assertRaises(cc.NotAuthorized):
            bad_table.drop()
            
        bad_view = bad_cloud.View(view)
        with self.assertRaises(cc.NotAuthorized):
            bad_view.rename('lily')
            
        with self.assertRaises(cc.NotAuthorized):
            bad_view.drop()
        
        bad_col = bad_cloud.Column(col)
        with self.assertRaises(cc.NotAuthorized):
            bad_col.rename('lacdulac')
            
        with self.assertRaises(cc.NotAuthorized):
            bad_col.modify('Integer')
            
        with self.assertRaises(cc.NotAuthorized):
            bad_col.drop()
            
        
            
    
    
def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestAuth))
    return suite

if __name__ == '__main__':
    unittest.main()
