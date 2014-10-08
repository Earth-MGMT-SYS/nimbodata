"""Module tests query functionality (select)."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys
import datetime
from pprint import pprint
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
        cols = [
            {'name':'pk','datatype':Text,'primary_key':True},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        self.table = cloud.create_table(self.db,'testTable',cols)
        self.values = [
            ('frank',2,'apple'),
            ('jerry',5,'orange'),
            ('ann',7,'fig'),
            ('francine',9,'tomato'),
        ]
        
        self.rowids = self.table.insert(self.values)
        
    def tearDown(self):
        """Drop the database."""
        self.db.drop()
        
    def _joinTable(self):
        """For the join tests, a second table with some values."""
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'z','datatype':Text}
        ]
        
        self.table2 = cloud.create_table(self.db,'jointable',cols)
        val2 = [
            ('jerry','sting'),
            ('ann','madonna'),
            ('francine','boy george')
        ]
        
        self.table2.insert(val2)
    
    def _joinSecond(self):
        """For the double-join test.  Another table with values."""
        cols = [
            {'name':'z','datatype':Text},
            {'name':'jj','datatype':Text},
        ]
        
        self.table3 = self.db.create_table('join2',cols)
        vals = [
            ('sting','vlappo'),
            ('madonna','crapding'),
            ('boy george','barsz'),
        ]
        self.table3.insert(vals)
        
    def _aggTable(self):
        """For the aggregation tests, a second table with some numbers."""
        cols2 = [
            {'name':'pk','datatype':Text},
            {'name':'orderno','datatype':Integer},
            {'name':'ordertotal','datatype':Float}
        ]
        
        val2 = [
            ('frank',0,20.00),
            ('frank',1,13.99),
            ('frank',2,12.15),
            ('jerry',0,21.11),
            ('jerry',1,22.22),
            ('jerry',2,33.33),
            ('ann',0,9.00),
            ('francine',0,99.09),
            ('francine',1,2.22)
        ]
        
        self.table2 = cloud.create_table(self.db,'aggtable',cols2)
        self.table2.insert(val2)
        
    def _castInteger(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text}
        ]
        
        vals = [
            ('a',1,'1'),
            ('b',2,'2'),
            ('c',3,'3')
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
        
    def _uniqueVals(self):
        cols = [
            {'name':'a','datatype':Integer}
        ]
        
        vals = [
            (1,),
            (1,),
            (2,),
            (3,),
        ]
        
        self.uqtable = self.db.create_table('cast_table',cols)
        self.uqtable.insert(vals)
        
    def _castIntArray(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':IntegerArray},
            {'name':'b','datatype':Text}
        ]
        
        vals = [
            ('b',[3,4],'[3,4]'),
            ('a',[1,2],'1,2'),
            ('c',[5,6],'5,6')
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
        
    def _castFloatArray(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':FloatArray},
            {'name':'b','datatype':Text}
        ]
        
        vals = [
            ('a',[1.1,2.2],'[1.1,2.2]'),
            ('b',[3.3,4.4],'3.3,4.4'),
            ('c',[5.5,6.6],'[ 5.5 , 6.6 ]')
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
        
    def _castTextArray(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':TextArray},
            {'name':'b','datatype':Text}
        ]
        
        vals = [
            ('a',['apple','bannana'],'apple,bannana'),
            ('b',['pie','cookies'],'[pie,cookies]')
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
        
    def _castFloat(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Float},
            {'name':'b','datatype':Text}
        ]
        
        vals = [
            ('a',1.1,'1.1'),
            ('b',2.2,'2.2'),
            ('c',3.3,'3.3')
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
        
    def _castText(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Text},
            {'name':'b','datatype':Text}
        ]
        
        vals = [
            ('a','1',1),
            ('b','2',2),
            ('c','3',3)
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
        
    def _castDate(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Text},
            {'name':'b','datatype':Date}
        ]
        
        vals = [
            ('a','1950-09-09',Date(1950,9,9)),
            ('b','1944-03-03',Date(1944,3,3)),
            ('c','1932-12-25',Date(1932,12,25))
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
        
    def _extractYear(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Date}
        ]
        
        vals = [
            ('a',1950,Date(1950,9,9)),
            ('b',1944,Date(1944,3,3)),
            ('c',1932,Date(1932,12,25))
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
        
    def _castTimestamp(self):
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Text},
            {'name':'b','datatype':Timestamp}
        ]
        
        vals = [
            ('a','1950-09-09:01:01',datetime.datetime(1950,9,9,1,1)),
            ('b','1944-03-03:02:02',datetime.datetime(1944,3,3,2,2)),
            ('c','1932-12-25:03:03',datetime.datetime(1932,12,25,3,3))
        ]
        
        self.cast_table = self.db.create_table('cast_table',cols)
        self.cast_table.insert(vals)
    
    #@unittest.skip('skip')
    def test_group(self):
        """Can we do a group by with an aggregate function?"""
        self._aggTable()
        cols = ['pk',MAX('ordertotal')]
        group_by = ['pk']
        
        view = cloud.select(
            self.table2,
            cols=cols,
            group_by=group_by,
            order_by='pk'
        )
        
        self.assertEqual(view[0][1],9.0)
        self.assertEqual(view[1][1],99.09)
        cols = ['pk',AVG('ordertotal')]
        
        view = cloud.select(
            self.table2,
            cols=cols,
            group_by=group_by,
            order_by='pk'
        )
        
        self.assertEqual(view[0][1],9.0)
        self.assertEqual(view[1][1],50.655)
    
    #@unittest.skip('skip')
    def test_function(self):
        """Can we do a function without a group by?"""
        self._aggTable()
        
        cols = [MAX('ordertotal')]
        result = cloud.select(self.table2,cols)
        self.assertEqual(result[0][0],99.09)
        
        cols = [MIN('ordertotal')]
        result = cloud.select(self.table2,cols)
        self.assertEqual(result[0][0],2.22)
        
        cols = [AVG('ordertotal')]
        result = cloud.select(self.table2,cols)
        self.assertEqual(result[0][0],25.9011111111111)
    
    #@unittest.skip('skip')
    def test_func_agg_view(self):
        self._aggTable()
        
        pk,ono,otot = self.table2.columns()
        cols = [MAX(otot)]
        
        view = self.db.create_view('testview',{
            'objid':self.table2,
            'cols':cols
        })
        
        #print [x['objid'] for x in view.columns()]
        
        result = cloud.select(view)
        self.assertEqual(result[0][0],99.09)
    
    #@unittest.skip('skip')
    def test_asinteger(self):
        """Can we select column of Integers typed as Text cast as Integer?"""
        self._castInteger()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,Integer(b)]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
            
    #@unittest.skip('skip')
    def test_asinteger_view(self):
        """Can we select column of Integers typed as Text cast as Integer?"""
        self._castInteger()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,Integer(b)]
        view = self.db.create_view('testview',{
            'objid':self.cast_table,
            'cols':cols
        })
        #self.assertEquals(
            #[x.info for x in view.columns()][2]['datatype'],'Integer'
        #)
        result = view.select()
        for row in result:
            self.assertEquals(row[1],row[2])
    
    #@unittest.skip('skip')
    def test_asinteger_array(self):
        """Can we select column of Integer Arrays typed as Text?"""
        self._castIntArray()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,IntegerArray(b)]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
            
    #@unittest.skip('skip')
    def test_asfloat(self):
        """Can we select column of floats typed as Text cast as float?"""
        self._castFloat()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,Float(b)]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
            
    #@unittest.skip('skip')
    def test_asfloat_array(self):
        """Can we select column of Integers typed as Text cast as Integer?"""
        self._castFloatArray()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,FloatArray(b)]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
            
    #@unittest.skip('skip')
    def test_astext(self):
        """Can we select column of integers cast as text?"""
        self._castText()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,Text(b)]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
    
    #@unittest.skip('skip')
    def test_astext_array(self):
        """Can we select column of Integers typed as Text cast as Integer?"""
        self._castTextArray()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,TextArray(b)]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
            
    #@unittest.skip('skip')
    def test_asdate(self):
        """Can we select column of dates typed as text cast as dates?"""
        self._castDate()
        pk,a,b = self.cast_table.columns()
        cols = [pk,Date(a,'YYYY-MM-DD'),b]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
            
    #@unittest.skip('skip')
    def test_astimestamp(self):
        """Can we select column of timestamps typed as text cast as timestamps?"""
        self._castTimestamp()
        pk,a,b = self.cast_table.columns()
        cols = [pk,Timestamp(a,'YYYY-MM-DD:HH:MI'),b]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
            
    #@unittest.skip('skip')
    def test_extract(self):
        """Can we select column of dates typed as text cast as dates?"""
        self._extractYear()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,extract(b,'year')]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[2])
    
    #@unittest.skip('skip')
    def test_extract_twice(self):
        """Can we select column of dates typed as text cast as dates?"""
        self._extractYear()
        pk,a,b = self.cast_table.columns()
        cols = [pk,a,b,extract(b,'year'),extract(b,'month')]
        result = cloud.select(self.cast_table,cols)
        for row in result:
            self.assertEquals(row[1],row[3])
            self.assertEquals(row[2].month,row[4])
    
    #@unittest.skip('skip')
    def test_unique(self):
        """Can we select column of dates typed as text cast as dates?"""
        self._uniqueVals()
        a = self.uqtable.columns()[0]
        cols = [unique(a)]
        result = self.uqtable.select(cols,order_by=[a])
        vals = [x[0] for x in result]
        self.assertEquals(vals,[1,2,3])
        

if __name__ == '__main__':
    unittest.main()
