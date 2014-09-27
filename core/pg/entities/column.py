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
            tblinfo=None,index=None,exp=None):
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
                try:
                    datatype = getattr(datatypes,str(datatype))
                except AttributeError:
                    raise TypeError(str(datatype)+ " is not a valid type.")
        
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
        
        # Needs cleanup
        if exp is not None:
            p = self.api.get_byid(parent)
            s = datatypes.Function().sql_exp(*exp)
            stmt = syntax.update_as(p['parent_objid'],p.objid,colid,s)
            controllers['ddl'].execute(stmt,params)
        
        controllers['ddl'].conn.commit()
        
        self.objid = colid
        
        return self
        
    def modify(self,params):
        """Change the type of a column."""
        if self['owner'] != self.session['user']:
            raise errors.NotAuthorized
        
        if 'datatype' in params:
            newtype = params['datatype']
            colinfo = self.info
            tblinfo = self.api.get_entity('Column')(objid=colinfo['parent_objid'])
            
            # Need to validate `newtype`
            mod_stmt = syntax.alter_column_type(
                tblinfo['parent_objid'],
                tblinfo['objid'],
                colinfo['objid'],
                newtype
            )
            
            try:
                controllers['ddl'].execute(mod_stmt)
            except errors.DataError:
                table = self.api.get_entity('Table')(tblinfo['objid'])
                result = table.select(['_adm-rowid',colinfo['objid']])
                out = []
                for row in result:
                    if newtype == 'Integer':
                        try:
                            if str(row[1])[0] not in ('123456789'):
                                out.append([row[0],None])
                            else:
                                out.append([row[0],int(row[1])])
                        except IndexError:
                            out.append([row[0],None])
                return out
            
            colinfo['datatype'] = newtype
            self._registry_insert(colinfo)
            
            controllers['ddl'].conn.commit()
            return self.objid
        
        print params
        return Entity.modify(self,params)
    
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



