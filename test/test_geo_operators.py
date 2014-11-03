
import unittest
import sys

sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import Text,Point, Line
from common.expressions import Join

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
class TestOperators(unittest.TestCase):
    
    def setUp(self):
        try:
            self.db = cloud.create_database('gop')
        except (cc.RelationExists,cc.IntegrityError):
            cloud.Database('gop').drop()
            self.db = cloud.create_database('gop')
        
        cols = [
            {'name':'label','datatype':Text},
            {'name':'geom','datatype':Line}
        ]
        
        self.table = self.db.create_table('geoop',cols)
        self.table2 = self.db.create_table('geoo2p',cols)
        
        self.A = Line([Point(1,1),Point(2,3)])
        self.B = Line([Point(2,1),Point(1,3)])
        self.C = Line([Point(3,1),Point(4,3)])
        self.D = Line([Point(4,1),Point(3,3)])
        self.E = Line([Point(1,4),Point(4,4)])
        
        values = [
            ['A',self.A],
            ['B',self.B],
            ['C',self.C],
            ['D',self.D],
            ['E',self.E]
        ]
        
        self.table.insert(values)
        self.table2.insert(values)
                
    def tearDown(self):
        self.db.drop()
    
    #@unittest.skip('skip')
    def test_contains(self):
        """Does the contains operator function work?"""
        label,geom = self.table.columns()
        wh = geom.contains(self.B)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),2)
        self.assertEquals(result.rows[0][0],'A')
        self.assertEquals(result.rows[1][0],'B')
        
    #@unittest.skip('skip')
    def test_contain_join(self):
        """Does the contains operator function work?"""
        label,geom = self.table.columns()
        l2,g2 = self.table2.columns()
        
        result = self.table.select(
            cols=[label],
            join=Join(self.table2,geom.intersects(g2))
        )
        # I need to actually test this... maybe... the syntax is right.

    #@unittest.skip('skip')
    def test_containedby(self):
        """Does the contained by operator function work?"""
        label,geom = self.table.columns()
        wh = geom.containedby(self.B)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),2)
        self.assertEquals(result.rows[0][0],'A')
        self.assertEquals(result.rows[1][0],'B')
    
    #@unittest.skip('skip')
    def test_samebbox(self):
        """Does the same bounding box operator function work?"""
        label,geom = self.table.columns()
        wh = geom.same_bbox(self.B)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),2)
        self.assertEquals(result.rows[0][0],'A')
        self.assertEquals(result.rows[1][0],'B')
        
    #@unittest.skip('skip')
    def test_overlap_or_left(self):
        """Does the overlap or left of operator function work?"""
        label,geom = self.table.columns()
        wh = geom.overlap_or_left(self.D)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),5)
        
        label,geom = self.table.columns()
        wh = geom.overlap_or_left(self.A)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),2)
        
    #@unittest.skip('skip')
    def test_overlap_or_right(self):
        """Does the overlap or right of operator function work?"""
        label,geom = self.table.columns()
        wh = geom.overlap_or_right(self.D)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),2)
        
        label,geom = self.table.columns()
        wh = geom.overlap_or_right(self.A)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),5)
    
    #@unittest.skip('skip')
    def test_overlap_or_above(self):
        """Does the overlap or above operator function work?"""
        label,geom = self.table.columns()
        wh = geom.overlap_or_above(self.A)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),5)
        
        label,geom = self.table.columns()
        wh = geom.overlap_or_above(self.E)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),1)
        
    #@unittest.skip('skip')
    def test_overlap_or_below(self):
        """Does the overlap or below operator function work?"""
        label,geom = self.table.columns()
        wh = geom.overlap_or_above(self.E)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),1)
        
        label,geom = self.table.columns()
        wh = geom.overlap_or_above(self.A)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),5)
    
    #@unittest.skip('skip')
    def test_leftof(self):
        """Does the left of operator function work?"""
        label,geom = self.table.columns()
        wh = geom.leftof(self.A)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),0)
        
        label,geom = self.table.columns()
        wh = geom.leftof(self.D)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),2)
        
    #@unittest.skip('skip')
    def test_rightof(self):
        """Does the right of operator function work?"""
        label,geom = self.table.columns()
        wh = geom.rightof(self.D)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),0)
        
        label,geom = self.table.columns()
        wh = geom.rightof(self.A)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),2)
    
    #@unittest.skip('skip')
    def test_below(self):
        """Does the below operator function work?"""
        label,geom = self.table.columns()
        wh = geom.below(self.A)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),0)
        
        label,geom = self.table.columns()
        wh = geom.below(self.E)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),4)
    
    #@unittest.skip('skip')
    def test_above(self):
        """Does the above operator function work?"""
        label,geom = self.table.columns()
        wh = geom.above(self.A)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),1)
        
        label,geom = self.table.columns()
        wh = geom.above(self.E)
        
        result = self.table.select(where=wh)
        self.assertEquals(len(result),0)
        

def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestOperators))
    return suite

if __name__ == '__main__':
    unittest.main()
