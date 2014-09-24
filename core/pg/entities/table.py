"""Module implements the PostgreSQL table for Nimbodata."""
# Copyright (C) 2014  Bradley Alan Smith


import StringIO
import csv
import datetime
import json

import shapely.geometry as geo
import shapely.wkt as wkt
import jsonpickle
import psycopg2

import common.entities.table as base_table

from .. import syntax, datatypes
from . import *
from common import tilecalc

class Table(base_table.Table,View):
    """PostgreSQL table as Nimbodata Entity."""
    
    tbl_reg = '_adm-tableregistry'
    _by_name = Entity._by_name
    
    def _start_colindex(self):
        """Get the next column index for the table."""
        stmt,params = syntax.select(
            "_adm-registries",
            "_adm-maxcolindex",
            ("maxindex",),('parent_objid','=',str(self.objid))
        )
        
        r = controllers['drc']._get_scalar(0,stmt,params)
        startIndex = 0 if r is None else r + 1
        return startIndex
        
    def create(self,parent_objid,name,cols):
        """Create the table in SQL then register it."""
        tblid = self._new_id()
        
        ent_args = {
            'parent_objid':parent_objid,
            'name':name,
            'owner':self.session['user'],
            'objid':tblid
        }
        
        Entity.create(self,ent_args)
        
        controllers['ddl'].conn.commit()
        controllers['ddl'].execute(syntax.create_managed_table(parent_objid,tblid))
        controllers['ddl'].conn.commit()
        self.objid = tblid
        if cols:
            self.add_columns(cols)
        self.objid = tblid
        controllers['ddl'].conn.commit()
        return self
        
    def drop(self):
        """"Drop the table in SQL the de-register it."""
        tblinfo = self.info
        Entity.drop(self)
        
        for x in self.columns():
            x.drop()
        
        stmt = syntax.drop_table(tblinfo['parent_objid'],self.objid)
        
        controllers['ddl'].execute(stmt)
        
        return True
    
    def add_index(self,col,unique=False):
        geocolnames = [x['name'] for x in self.geo_columns()]
        colinfo = self.api.get_entity('Column')(col).info
        index_type = 'GIST' if colinfo['name'] in geocolnames else None
        dbid,tblname = self.info['parent_objid'],self.info['name']
        tblid = self.info['objid']
        tblowner = self.info['owner']
        stmt = syntax.add_index(
            dbid,tblid,self._new_indid(),colinfo['objid'],unique,index_type
        )
        controllers['ddl'].execute(stmt)
        controllers['ddl'].conn.commit()
        return self.info
    
    def add_columns(self,cols):
        """Add columns to the table."""
        dbid,tblname = self.info['parent_objid'],self.info['name'],
        tblowner = self.info['owner']
        stmts = []
        startIndex = self._start_colindex()
        for i,col in enumerate(cols,startIndex):
            self.api.get_function('Column','create')(self.objid,index=i,**col)
        controllers['ddl'].execute_many(stmts)
        controllers['ddl'].conn.commit()
        return
        
    def columns(self):
        """Get a listing of columns for the table."""
        tblid = str(self.objid)
         
        cols = (
            'name',
            'owner',
            'objid',
            'parent_objid',
            'entitytype',
            'datatype',
            'weight',
            'alias'
        )
                
        header = [{'name':x,'weight':i} for i,x in enumerate(cols)]

        stmt, params = syntax.select(
            self.schema,
            self.ent_info,
            where = [
                ('parent_objid','=',tblid),
                ('name','!=','rowid'),
                ('entitytype','=','Column')
            ],
            order_by = ['weight']
        )
        
        infos = list(controllers['drc'].execute(stmt,params))
        retVal = []
        
        for i in infos:
            retVal.append(self.api.get_entity(i['entitytype'])(objid=i['objid']))
            
        return retVal
        
    def _process_row(self,dtypes,values):
        """Process a row before inserting it."""
        retVal = {}
        for i, val in enumerate(zip(dtypes,values)):
            retVal[str(i)] = self._process_item(i,*val)
        return retVal
    
    def _process_item(self,i,dtype,val):
        """Process an individual item before inserting it."""
        if dtype == 'rowid':
            return val
        typeobj = getattr(datatypes,dtype)
        if isinstance(typeobj,datatypes.Geographic):
            if isinstance(val,basestring):
                val = wkt.loads(val)
            else:
                return val
        if isinstance(val,basestring) and not self._isid(val):
            try:
                return jsonpickle.decode(val)
            except:
                pass
        elif dtype == 'Json':
            return json.dumps(val)
        return val
    
    def _new_rowid(self):
        """Gets a new rowid for an inserted row."""
        return 'row-'+str(uuid()).replace('-','')
        
    def _new_indid(self):
        """Gets a new rowid for an inserted row."""
        return 'ind-'+str(uuid()).replace('-','')
    
    def _insert_dict(self,tblid,values,rowid=None):
        """Insert a row where the input is a dict."""
        tblinfo = self.info
        colinfo = Table(objid=tblid).columns()
        geocols = [x for x in colinfo if x['datatype'].startswith('geography')]
        dbid,tblname = tblinfo['parent_objid'],tblinfo['name']
        colnames = [x['name'] for x in colinfo]
        decoder = dict((x['name'],x['objid']) for x in colinfo)
        decoder['_adm-rowid'] = '_adm-rowid'
        sub = {}
        stmt = """INSERT INTO %(tqn)s (%(headers)s) VALUES (%(vals)s)"""
        sub['tqn'] = syntax.get_tqn(dbid,tblid)
        headers = ['"'+decoder[x]+'"' for x in values.keys()]
        sub['headers'] = ', '.join(headers)
        sub['vals'] = ', '.join('%('+col+')s' for col in values.keys())
        stmt = stmt % sub
        values['_adm-rowid'] = self._new_rowid() if rowid is None else rowid
        r = controllers['dml'].execute(stmt,values)
        return values['_adm-rowid']
    
    def _insert_row(self,tblid,values,rowid=None):
        """Insert a row where the input is a list."""
        tblinfo = self.info
        colinfo = Table(objid=tblid).columns()
        dtypes = ['rowid']+[x['datatype'] for x in colinfo]
        dbid,tblname = tblinfo['parent_objid'],tblinfo['name']
        stmt = """INSERT INTO %(tqn)s VALUES (DEFAULT,%(vals)s)"""
        sub = {}
        sub['tqn'] = syntax.get_tqn(dbid,tblid)
        values = [self._new_rowid() if rowid is None else rowid] + list(values)
        placeholders = ('%('+str(x)+')s' for x in range(len(values)))
        sub['vals'] = ', '.join(placeholders)
        insVals = self._process_row(dtypes,values)
        try:
            r = controllers['dml'].execute(stmt%sub,insVals)
        except psycopg2.DataError as e:
            print insVals
            raise e
        return values[0]
        
    def insert_file(self,fobj,cols=None,header=True,fallback=True,errors=None):
        tqn = '''"%s"."%s"''' % (self['parent_objid'],self)
        fobj.seek(0)
        
        if cols is None:
            cols = ['"'+x['objid']+'"' for x in self.columns()]
        with controllers['dml'].conn.cursor() as cur:
            try:
                cur.copy_from(fobj, tqn, columns=cols)
                controllers['dml'].conn.commit()
            except psycopg2.DataError as e:
                controllers['dml'].conn.rollback()
                fobj.seek(0)
                
            try:
                cur.copy_from(fobj, tqn, sep=',',columns=cols)
                controllers['dml'].conn.commit()
                return errors
            except psycopg2.DataError as e:
                controllers['dml'].conn.rollback()
            
            fobj.seek(0)
            s = StringIO.StringIO()
            w = csv.writer(s)
            for row in csv.reader(fobj):
                w_row = [val.replace(',','\,') for val in row]
                w.writerow(w_row)
            s.seek(0)
            
            try:
                cur.copy_from(s, tqn, sep=',',columns=cols)
                controllers['dml'].conn.commit()
                return
            except psycopg2.DataError as e:
                controllers['dml'].conn.rollback()
                raise e
                bad_line = int(e.diag.context.split(' ')[3].replace(':',''))
            
            fobj.seek(0)
            s = StringIO.StringIO()
            w = csv.writer(s)
            if errors is None:
                errors = []
            rowlen = len(cols)
            for i,row in enumerate(csv.reader(fobj)):
                if i == bad_line - 1:
                    errors.append(row)
                    continue
                else:
                    w.writerow(row)
            s.seek(0)
            
            return self.insert_file(
                s,cols=cols,header=header,fallback=fallback,errors=errors
            )

    def insert(self,values,rowid=None):
        """Insert the row or rows into the table."""
        childTypes = (tuple,list,dict)
        tblid = str(self.objid)
        if isinstance(values,dict):
            rowid = self._insert_dict(tblid,values,rowid)
            controllers['dml'].conn.commit()
            return rowid
        elif any(isinstance(values[0],type_) for type_ in childTypes):
            # Single recursion via comprehension
            rowids = [self.insert(row,rowid) for row in values]
            controllers['dml'].conn.commit()
            return rowids
        else:
            rowid = self._insert_row(tblid,values,rowid)
            controllers['dml'].conn.commit()
            return rowid
    
    def update(self,tblid,rowid,new_values):
        """Update a row specified by rowid."""
        self.insert(tblid,new_values,rowid)

