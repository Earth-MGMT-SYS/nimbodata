"""Module tests query functionality (select)."""
# Copyright (C) 2014  Bradley Alan Smith

import unittest
import sys
sys.path.append('../')

import config_cloud as cfg
from core.pg.datatypes import Text,Integer,Float

target = 'rest'

if target == 'local':
    import core.cloud as cc
    cloud = cc.Cloud(cfg.user)
elif target == 'rest':
    sys.path.append('../client')
    import pyclient
    cloud = pyclient.connect("http://localhost:5000",cfg.user)

class TestSelect(unittest.TestCase):
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
    
    def _aliasTable(self):
        """Create a table with columns with aliases."""
        cols2 = [
            {'name':'pk','alias':'P K','datatype':Text},
            {'name':'orderno','datatype':Integer},
            {'name':'ordertotal','alias':'Order Total','datatype':Float}
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
        
        self.a_table = cloud.create_table(self.db,'aggtable',cols2)
        self.a_rows = self.a_table.insert(val2)
    
    #@unittest.skip('skip')
    def test_star(self):
        """Can we select * from a table?"""
        result = cloud.select(self.table)
        self.assertEqual(len(result.header),3)
        
        result = self.table.select()
        self.assertEqual(len(result.header),3)
        
        colnames = [x['name'] for x in result.header]
        self.assertEqual(['pk','a','b'],colnames)
   
    #@unittest.skip('skip')
    def test_target(self):
        """Can we select specified columns from a table? """
        result = cloud.select(self.table,cols=['pk','b'])
        self.assertEqual(len(result.header),2)
        colnames = [x['name'] for x in result.header]
        self.assertEqual(['pk','b'],colnames)
    
    #@unittest.skip('skip')
    def test_target_view(self):
        """Can we select columns from a view?"""
        self._aggTable()
        view = cloud.create_view(self.db,"testview",{
            'viewid':self.table2,
            'cols':['pk','orderno'],
            'order_by':['pk']
        })
        
        results = cloud.select(view)
        self.assertEquals(results[0]['pk'], 'ann')
        
        colnames = [x['name'] for x in results.header]
        self.assertEqual(['pk','orderno'],colnames)
        
        cols = view.columns()
        self.assertEquals(cols[0]['name'], 'pk')
        self.assertEquals(cols[1]['name'], 'orderno')
    
    #@unittest.skip('skip')
    def test_order(self):
        """Can we order the output with various syntax options? """
        results = cloud.select(self.table,order_by='pk')
        self.assertEqual(len(results),4)
        self.assertEqual(results[0][0],'ann')
        self.assertEqual(results[2][0],'frank')
        
        results = cloud.select(self.table,order_by=['pk'])
        self.assertEqual(len(results),4)
        self.assertEqual(results[0][0],'ann')
        self.assertEqual(results[2][0],'frank')
    
    #@unittest.skip('skip')
    def test_limit(self):
        """Can we limit the number of result rows?"""
        results = cloud.select(self.table,limit=2)
        self.assertEqual(len(results),2)
    
    #@unittest.skip('skip')
    def test_where(self):
        """Can we do basic where filters?"""        
        pk, a, b = self.table.columns()
        
        where = a < 9
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),3)
        
        where = pk == 'ann'
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),1)
        
        where = [a < 9,a > 2]
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),2)
        
    #@unittest.skip('skip')
    def test_single_where_syntax(self):
        """Can we do where queries in each syntax option?"""
        pk, a, b = self.table.columns()
                
        where = "a < 9"
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),3)
        where = ('a','<',9)
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),3)
        where = a < 9
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),3)
        
        where = "pk = ann"
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),1)
        where = ('pk','=','ann')
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),1)
        where = pk == 'ann'
        results = cloud.select(self.table,where = where)
        self.assertEqual(len(results),1)
    
    #@unittest.skip('skip')
    def test_where_twocols(self):
        """Test where statements comparing two columns."""
        self._aggTable()
        pk, orderno, ordertotal = self.table2.columns()
        
        where = orderno > ordertotal
        results = cloud.select(self.table2,where = where)
        self.assertEqual(len(results),0)
        
        where = ordertotal > orderno
        results = cloud.select(self.table2,where = where)
        self.assertEqual(len(results),9)

    #@unittest.skip('skip')
    def test_where_all(self):
        """Can we do an all query with the `all`, `any`, `none` approach?"""
        pk, a, b = self.table.columns()
        
        where = {
            'all':[a < 9,a > 2],
            'any':[],
            'none':[]
        }
        
        results = cloud.select(self.table,where = where,order_by='pk')
        self.assertEqual(len(results),2)
        self.assertEqual(results[0][0],'ann')
        
    #@unittest.skip('skip')
    def test_where_and(self):
        """Can we use the overridden & operator?"""
        pk, a, b = self.table.columns()
        
        where = ((a < 9) & (a > 2))
        
        results = cloud.select(self.table,where = where,order_by='pk')
        self.assertEqual(len(results),2)
        self.assertEqual(results[0][0],'ann')
    
    #@unittest.skip('skip')
    def test_where_or(self):
        """Can we use the overridden | operator?"""
        pk, a, b = self.table.columns()
        
        where = ((a == 9) | (a == 2))
        
        results = cloud.select(self.table,where = where,order_by='pk')
        self.assertEqual(len(results),2)
        self.assertEqual(results[0][0],'francine')
        
    #@unittest.skip('skip')
    def test_where_any(self):
        """Can we use operators inside an any literal?"""
        pk, a, b = self.table.columns()
        
        where = {
            'any':[pk == 'ann',pk == 'francine']
        }
        
        results = cloud.select(self.table,where = where,order_by='pk')
        self.assertEqual(len(results),2)
        self.assertEqual(results[0][0],'ann')
    
    #@unittest.skip('skip')
    def test_where_all_any(self):
        """Can we do a query with both `all` and `any`?"""
        pk, a, b = self.table.columns()
        
        where = {
            'all':[a < 9 ,a > 2],
            "any":[b == 'apple', b == 'fig']
        }
        
        results = cloud.select(self.table,where = where,order_by='pk')
        self.assertEqual(len(results),1)
        self.assertEqual(results[0][0],'ann')
    
    #@unittest.skip('skip')
    def test_where_all_any_none(self):
        """Can we do an `all`, `any`, `none` query?"""
        pk, a, b = self.table.columns()
        
        where = {
            'all':[a > 1, a < 9, pk != 'jerry'],
            "any":[b == 'apple', b == 'orange']
        }
        
        results = cloud.select(self.table,where = where,order_by='pk')
        self.assertEqual(len(results),1)
        self.assertEqual(results[0][0],'frank')
        
    #@unittest.skip('skip')
    def test_join(self):
        """Can we do a simple inner join?"""
        self._joinTable()
        join = (self.table2,"jointable.pk = testTable.pk")
        results = cloud.select(self.table,join=join)
        self.assertEqual(len(results),3)
    
    #@unittest.skip('skip')
    def test_where_order(self):
        """Can we do a where filter and order the results?"""
        pk, a, b = self.table.columns()
        where = [a < 9, a > 2]
        results = cloud.select(self.table,where = where, order_by='pk')
        self.assertEqual(len(results),2)
        self.assertEqual(results[0][0],'ann')
        self.assertEqual(results[1][0],'jerry')
    
    #@unittest.skip('skip')
    def test_where_order_limit(self):
        """Can we do a where filter and order and limit the results?"""
        pk, a, b = self.table.columns()
        where = [a < 9, a > 2]
        results = cloud.select(self.table,where = where, order_by='pk', limit=1)
        self.assertEqual(len(results),1)
        self.assertEqual(results[0][0],'ann')
    
    #@unittest.skip('skip')
    def test_where_order_limit_cols(self):
        """Can we specify the output columns, where filter, order and limit?"""
        pk, a, b = self.table.columns()
        where = [a < 9, a > 2]
        view = cloud.select(self.table,cols=['b','pk'],where = where, order_by='pk', limit=1)
        self.assertEqual(len(view),1)
        self.assertEqual(view[0][1],'ann')
        self.assertEqual(view[0][0],'fig')
    
    #@unittest.skip('skip')
    def test_where_join(self):
        """Can we do a where filter on a join query?"""
        pk, a, b = self.table.columns()
        self._joinTable()
        where = a == 7
        join = (self.table2,"jointable.pk = testTable.pk")
        results = cloud.select(self.table,join=join,where=where)
        self.assertEqual(len(results),1)
        self.assertEqual(results[0][0],'ann')
    
    #@unittest.skip('skip')
    def test_where_join_order(self):
        """Can we do a where filter on a join query and order the results?"""
        self._joinTable()
        pk, a, b = self.table.columns()
        where = a < 9
        join = (self.table2,"jointable.pk = testTable.pk")
        results = cloud.select(self.table,join=join,where=where,order_by='testTable.pk')
        self.assertEqual(len(results),2)
        self.assertEqual(results[1]['jointable.z'],'sting')
    
    #@unittest.skip('skip')
    def test_where_join_limit(self):
        """Can we do a where filter on a join query and limit the results?"""
        self._joinTable()
        pk, a, b = self.table.columns()
        where = a < 9
        join = (self.table2,"jointable.pk = testTable.pk")
        view = cloud.select(self.table,join=join,where=where,limit=1)
        self.assertEqual(len(view),1)
        self.assertEqual(len(view[0]),5)
    
    #@unittest.skip('skip')
    def test_where_join_order_limit(self):
        """Can we do a where on a join query, limit and order the results?"""
        self._joinTable()
        pk, a, b = self.table.columns()
        where = a < 9
        join = (self.table2,"jointable.pk = testTable.pk")
        
        view = cloud.select(
            self.table,
            join=join,
            where=where,
            order_by='testTable.pk',
            limit=1
        )
        
        self.assertEqual(len(view),1)
        self.assertEqual(view[0]['jointable.z'],'madonna')
    
    #@unittest.skip('skip')
    def test_group(self):
        """Can we do a group by with an aggregate function?"""
        self._aggTable()
        cols = ['pk',('max','ordertotal')]
        group_by = ['pk']
        
        view = cloud.select(
            self.table2,
            cols=cols,
            group_by=group_by,
            order_by='pk'
        )
        
        self.assertEqual(view[0][1],9.0)
        self.assertEqual(view[1][1],99.09)
        cols = ['pk',('avg','ordertotal')]
        
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
        
        cols = [('max','ordertotal')]
        result = cloud.select(self.table2,cols)
        self.assertEqual(result[0][0],99.09)
        
        cols = [('min','ordertotal')]
        result = cloud.select(self.table2,cols)
        self.assertEqual(result[0][0],2.22)
        
        cols = [('avg','ordertotal')]
        result = cloud.select(self.table2,cols)
        self.assertEqual(result[0][0],25.9011111111111)
    
    #@unittest.skip('skip')
    def test_byid(self):
        """Can we fetch a row by rowid?"""
        for row,rowid in zip(self.values,self.rowids):
            byid = cloud.get_byrowid(self.table,rowid)
            for act,ret in zip(byid,row):
                self.assertEquals(act[1],ret)

    #@unittest.skip('skip')
    def test_byid_alias(self):
        """Can we fetch a row by rowid using the aliases?"""
        self._aliasTable()
        for rowid in self.a_rows:
            byid = cloud.get_byrowid(self.a_table,rowid,True)
            self.assertEqual(byid[0][0],'P K')
            self.assertEqual(byid[1][0],'orderno')
            self.assertEqual(byid[2][0],'Order Total')
    
    #@unittest.skip('skip')
    def test_getarray(self):
        """Can we fetch an array?"""
        self._aggTable()
        result = cloud.get_array(
            self.table2,
            'ordertotal',
            order_by=['ordertotal']
        )
        self.assertEquals(result[0],2.22)
        result = cloud.get_array(
            self.table2,
            ('max','ordertotal'),
        )
        self.assertEquals(result[0],99.09)
        self.assertEquals(len(result),1)        

def getTests(cls):
    return unittest.TestLoader().loadTestsFromTestCase(cls)

def suite():
    suite = unittest.TestSuite()
    suite.addTest(getTests(TestSelect))
    return suite

if __name__ == '__main__':
    unittest.main()
