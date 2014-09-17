"""Module tests geographic functionality."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys

sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import Text,Point

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
class TestPoints(unittest.TestCase):
    """Test the geographic functionality."""
    
    def setUp(self):
        """Create the database, table and insert some values."""
        try:
            self.db = cloud.create_database('selectdb')
        except (cc.RelationExists,cc.IntegrityError):
            cloud.Database('selectdb').drop()
            self.db = cloud.create_database('selectdb')
        
        cols = [
            {'name':'home','datatype':Text},
            {'name':'poi','datatype':Point}
        ]
        
        self.table = cloud.create_table(self.db,'geotable',cols)
        
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
    
    def tearDown(self):
        """Drop the database"""
        self.db.drop()
    
    #@unittest.skip('skip')
    def test_basics(self):
        """Can we get a feature tile, does it have the expected data?"""
        tile = self.table.tile(0,0,0)
        self.assertEqual(len(tile['features']),4)
        
        cols = self.table.columns()
        
        self.assertEquals(cols[0]['name'],'home')
        self.assertEquals(cols[1]['name'],'poi')
        
        points = cloud.select(self.table)
        self.assertEquals(len(points.rows),4)
        
        view = self.db.create_view('testview',{'viewid':self.table})
        
        cols = view.columns()
        
        self.assertEquals(cols[0]['name'],'home')
        self.assertEquals(cols[1]['name'],'poi')
        
        results = view.select()
        self.assertEquals(len(results.rows),4)
           
        
    #@unittest.skip('skip')
    def test_basics_view(self):
        """Create a view of geographic data and get the features."""
        view = cloud.create_view(self.db,'GeoView',{
            'viewid':self.table,
            'cols':['home','poi']
        })
        
        viewcols = view.columns()
        self.assertEquals(viewcols[0]['name'],'home')
        self.assertEquals(viewcols[1]['name'],'poi')
        
    #@unittest.skip('skip') # Only works local
    def test_get_tile_ids(self):
        """Get the rowids corresponding to a tile, and get those features."""
        geotable = self.table
        single_rowid = geotable.tile_rowids(841,1565,12)
        self.assertEqual(len(single_rowid),1)
        features = geotable.features(single_rowid)
        
        features = geotable.features(self.rowids)
        self.assertEqual(len(features['features']),4)
        
        


def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestPoints))
    return suite

if __name__ == '__main__':
    unittest.main()
