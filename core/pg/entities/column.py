"""Module implements the PostgreSQL table column."""
# Copyright (C) 2014  Bradley Alan Smith

import common.entities.column as base_column
import common.errors as errors

from .. import syntax
from .. import datatypes
from . import *

class Column(base_column.Column,Entity):
    """Column in a table, referenced by views.  Can be used in where filter."""
    
    def _start_colindex(self,tblid):
        """Next column index, which may be zero if there are no columns."""
        stmt,params = syntax.select(
            "_adm-registries",
            "_adm-maxcolindex",
            ("maxindex",),('tblid','=',tblid)
        )
        
        r = controllers['ddl']._get_scalar(0,stmt,params)
        startIndex = 0 if r is None else r + 1
        return startIndex
    
    def create(self,parent,name,datatype,alias=None,primary_key=None,
            tblinfo=None,index=None):
        """Create the column in SQL, register it."""
        if tblinfo is None:
            try:
                tblinfo = parent.info
            except AttributeError:
                objid = str(parent)
        
                stmt, params = syntax.select(self.schema,
                                             self.ent_info,
                                             where = ('objid','=',objid))
                
                controllers['ddl'].conn.commit()
                tblinfo = dict(controllers['ddl']._get_first(stmt, params))
                
        if index is None:
            index = self._start_colindex(parent)
        
        dbid,tblname = tblinfo['parent_objid'],tblinfo['name']
        tblowner = tblinfo['owner']
        
        colid = self._new_id()
        
        if isinstance(datatype,basestring):
            if datatype.startswith('datatype:'):
                datatype = datatype[9:]
            else:
                datatype = datatype
        else:
            datatype = type(datatype).__name__
        
        regVals = {
            'parent_objid':parent,
            'weight':index,
            'name':name,
            'alias':alias,
            'datatype':datatype,
            'owner':tblowner,
            'objid':colid
        }
        
        Entity.create(self,regVals)
        regVals['qtn'] = str(dbid)+'"."'+str(parent)
        
        if not isinstance(datatype,datatypes.Datatype):
            try:
                datatype = getattr(datatypes,str(datatype)[9:])
            except AttributeError:
                datatype = getattr(datatypes,str(datatype))
        
        try:
            dt_sql = datatype.sql_create()
        except TypeError:
            dt_sql = datatype.sql_create
        
        stmt = syntax.add_column(
            dbid,
            parent,
            colid,
            dt_sql,
            primary_key
        )
        
        controllers['ddl'].execute(stmt)
        controllers['ddl'].conn.commit()
        
        self.objid = colid
        
        return self
        
    def modify(self,newtype):
        """Change the type of a column."""
        if self['owner'] != self.session['user']:
            raise errors.NotAuthorized
        colinfo = self.info
        tblinfo = self.api.get_entity('Column')(objid=colinfo['parent_objid'])
        
        # Need to validate `newtype`
        mod_stmt = syntax.alter_column_type(
            tblinfo['parent_objid'],
            tblinfo['objid'],
            colinfo['objid'],
            newtype
        )
        
        controllers['ddl'].execute(mod_stmt)
        
        colinfo['datatype'] = newtype
        self._registry_insert(colinfo)
        
        controllers['ddl'].conn.commit()
        return self.objid
    
    def drop(self):
        """Drop the column from the table."""
        colinfo = self.info
        Entity.drop(self)        
        
        tblinfo = self.api.get_entity('Table')(objid=colinfo['parent_objid'])
        
        stmt = syntax.drop_column(
            tblinfo['parent_objid'],
            tblinfo['objid'],self.objid
        )
                
        try:
            controllers['ddl'].execute(stmt)
        except psycopg2.ProgrammingError:
            pass
        
        return True



