"""Module tests the instantiation of database entities."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys
from pprint import pprint

from shapely.geometry import *
import psycopg2

sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import Text,Integer, Float, Date
from common.expressions import extract, MAX, generate_series

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient as cc
    cloud = cc.connect("http://localhost:5000",cfg.user)

class TestViews(unittest.TestCase):
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
    
    def _datestable(self):
        cols = [
            {'name':'num','datatype':Integer},
            {'name':'name','datatype':Text}
        ]
        
        self.table = self.db.create_table('Colstufffff',cols)
        values = [
            (1,'a'),
            (2,'b'),
            (3,'c')
        ]
        self.table.insert(values)
        
        
        cols = [
            {'name':'num','datatype':Integer},
            {'name':'obd','datatype':Date},
            {'name':'value','datatype':Float},
        ]
        self.jtbl = self.db.create_table('Colll',cols)
        values = [
            (1,Date(1950,1,1),10.5),
            (1,Date(1950,6,6),21.1),
            (1,Date(1990,1,1),88.8),
            (1,Date(1990,6,6),33.3),
            (2,Date(1950,1,1),23.3),
            (2,Date(1950,6,6),13.3),
            (2,Date(1990,1,1),39.4),
            (2,Date(1990,6,6),93.7),
            (3,Date(1950,1,1),23.3),
            (3,Date(1950,6,6),13.3),
            (3,Date(1990,1,1),39.4),
            (3,Date(1990,6,6),93.7),
        ]
        self.jtbl.insert(values)
    
    #@unittest.skip('skip')
    def test_view_metadata(self):
        """Can we create and query from a view?"""
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        self.table = self.db.create_table('Colstuff',cols)
        view = self.db.create_view('Cloudy',{'objid':self.table})
        check_view = self.db.view('Cloudy')
        self.assertEquals(view.objid,check_view.objid)
        views = self.db.views()
        self.assertEquals(len(views),1)
        self.assertEquals(views[0]['objid'],view.objid)
        viewcols = view.columns()
        self.assertEquals(len(viewcols),3)
        self.assertEquals(viewcols[0]['name'],'pk')
        self.assertEquals(viewcols[1]['name'],'a')
        self.assertEquals(viewcols[2]['name'],'b')
        
    #@unittest.skip('skip')
    def test_tableview(self):
        """Can we create a view on a table rather than db?"""
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        self.table = self.db.create_table('Colstuff',cols)
        values = [
            ('frank',2,'1'),
            ('jerry',5,'2'),
            ('ann',7,'3'),
            ('francine',9,'4'),
        ]
        
        self.table.insert(values)
        
        view = self.table.create_view('ringbat',{'objid':self.table})
        check_view = self.table.View('ringbat')
        self.assertEquals(view.objid,check_view.objid)
        views = self.table.views()
        self.assertEquals(len(views),1)
        self.assertEquals(views[0]['objid'],view.objid)
        viewcols = view.columns()
        self.assertEquals(len(viewcols),3)
        self.assertEquals(viewcols[0]['name'],'pk')
        self.assertEquals(viewcols[1]['name'],'a')
        self.assertEquals(viewcols[2]['name'],'b')
        view.select()
        
    #@unittest.skip('skip')
    def test_from_function(self):
        """Can we select from a function instead of a relation? """
        view = self.db.create_view('sssrrrsly',
            {'objid':generate_series(Date(2010,1,1),Date(2013,1,1))}
        )
        result = view.select()
        self.assertEquals(len(result),1097)
        self.assertEquals(type(result[0][0]).__name__,'date')
    
    #@unittest.skip('skip')
    def test_view_insert_select(self):
        """Can we select from a view reliably after inserts?"""
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        self.table = self.db.create_table('Colstuff',cols)
        values = [
            ('frank',2,'1'),
            ('jerry',5,'2'),
            ('ann',7,'3'),
            ('francine',9,'4'),
        ]
        
        self.table.insert(values)
        
        view = self.db.create_view('Cloudy',{
            'objid':self.table,
            'order_by':['pk']
        })
        result = cloud.select(view)
        self.assertEquals(result[0]['a'],7)
        result = cloud.select(view)
        self.assertEquals(result[0]['pk'],'ann')
        
        temp = self.db.create_view(
            'With a chance of Meatwad',
            {
                'objid':self.table,
                'order_by':'pk'
            },
            temporary = True
        )
        result = cloud.select(temp)
        self.assertEquals(result[0]['a'],7)
        result = cloud.select(temp)
        self.assertEquals(result[0]['pk'],'ann')
        
    #@unittest.skip('skip')
    def test_materialized_view(self):
        """Can we select from a view reliably after inserts?"""
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Text},
        ]
        
        self.table = self.db.create_table('sadsds',cols)
        values = [
            ('frank',2,'1'),
            ('jerry',5,'2'),
            ('ann',7,'3'),
            ('francine',9,'4'),
        ]
        
        self.table.insert(values)
        view = self.db.create_view('Casdasd',{
                'objid':self.table,
                'order_by':'pk'
            },materialized=True)
        result = cloud.select(view)
        self.assertEquals(result[0]['a'],7)
        result = cloud.select(view)
        self.assertEquals(result[0]['pk'],'ann')
        
    #@unittest.skip('skip')
    def test_view_expression(self):
        """Can we use an expression when creating a view?"""
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Integer},
        ]
        
        self.table = self.db.create_table('JustColstuff',cols)
        values = [
            ('a',2,4),
            ('b',5,10),
            ('c',7,14),
            ('d',9,18),
        ]
        
        self.table.insert(values)
        pk,a,b = self.table.columns()
        viewcols = [pk,a * 2,b]
        view = self.db.create_view('Espresso',{
            'objid':self.table,
            'cols':viewcols
        })
        result = view.select()
        for row in result:
            self.assertEquals(row[1],row[2])
    
    #@unittest.skip('skip')
    def test_groupview(self):
        
        self._datestable()
        nnum,obd,value = self.jtbl.columns()
        num, name = self.table.columns()
        
        view = self.db.create_view('Ss',{
            'objid':self.jtbl,
            'cols':[name,num,extract(obd,'year'),extract(obd,'month'),MAX(value)],
            'join':(self.table,(nnum,'=',num)),
            'group_by':[name,num,extract(obd,'year'),extract(obd,'month')],
            'order_by':[name,num,extract(obd,'year'),extract(obd,'month')],
        })
    
    #@unittest.skip('skip')
    def test_view_expression_join(self):
        """Can we use an expression when creating a view?"""
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Integer},
            {'name':'b','datatype':Integer},
        ]
        
        self.table = self.db.create_table('JustColstuff',cols)
        values = [
            ('a',2,4),
            ('b',5,10),
            ('c',7,14),
            ('d',9,18),
        ]
        
        self.table.insert(values)
        
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'k','datatype':Integer},
        ]
        
        jtbl = self.db.create_table('JoinTest',cols)
        values = [
            ('a',4),
            ('b',10),
            ('c',14),
            ('d',18),
        ]
        
        jtbl.insert(values)
        
        pk,a,b = self.table.columns()
        j,k = jtbl.columns()
        viewcols = [pk, a, k / 2]
        view = self.db.create_view('Espresso',{
            'objid':self.table,
            'cols':viewcols,
            'join':(jtbl,(pk,'=',j))
        })
        result = view.select()
        for row in result:
            self.assertEquals(row[1],row[2])
            
        viewcols = [pk, a, k]
        view = self.db.create_view('AlsoRan',{
            'objid':self.table,
            'cols':viewcols,
            'join':(jtbl,(pk,'=',j))
        })
        result = view.select()
        for row in result:
            self.assertEquals(2*row[1],row[2])
    
    #@unittest.skip('skip')
    def test_nested_views(self):
        cols = [{'name':'a','datatype':Integer}]
        
        self.table = self.db.create_table('GettinNesty',cols)
        sel = {'objid':self.table}
        v1 = self.table.create_view('n1',sel)
        v2 = v1.create_view('n2',sel)
        v3 = v2.create_view('n3',sel)
        sel = {'objid':v3}
        v4 = v3.create_view('n4',sel)
        v4.select()
    
    #@unittest.skip('skip')
    def test_view_twodate(self):
        """Can we use an expression when creating a view?"""
        cols = [
            {'name':'pk','datatype':Text},
            {'name':'a','datatype':Date},
            {'name':'b','datatype':Integer},
            {'name':'c','datatype':Integer},
        ]
        
        self.table = self.db.create_table('JustColstuff',cols)
        values = [
            ('a',Date(1950,1,1),1950,1),
            ('b',Date(1933,3,3),1933,3),
            ('c',Date(1944,6,2),1944,6),
            ('d',Date(1901,7,7),1901,7),
        ]
        
        self.table.insert(values)
        pk,a,b,c = self.table.columns()
        viewcols = [pk,a,b,c,extract(a,'year'),extract(a,'month')]
        view = self.db.create_view('Espresso',{
            'objid':self.table,
            'cols':viewcols
        })
        result = view.select()
        for row in result:
            self.assertEquals(row[2],row[4])
            self.assertEquals(row[3],row[5])
        


if __name__ == '__main__':
    unittest.main()
