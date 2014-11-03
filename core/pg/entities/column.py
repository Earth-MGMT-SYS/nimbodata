"""Module implements the PostgreSQL table column."""
# Copyright (C) 2014  Bradley Alan Smith

import common.entities.column as base_column
import common.errors as errors

from .. import syntax
from .. import datatypes
from .. import expressions
from . import *

class Column(base_column.Column,Entity):
    """Column in a table, referenced by views.  Can be used in where filter."""
            
    def __init__(self,*args,**kwargs):
        if 'func' in kwargs:
            self.func = kwargs['func']
            del(kwargs['func'])
        return Entity.__init__(self,*args,**kwargs)
    
    def _start_weight(self,tblid):
        """Next column weight, which may be zero if there are no columns."""
        stmt,params = syntax.select(
            "_adm-registries",
            "_adm-maxcolindex",
            ("maxindex",),('tblid','=',tblid)
        )
        
        r = controllers['ddl']._get_scalar(0,stmt,params)
        startIndex = 0 if r is None else r + 1
        return startIndex
    
    def create(self,parent,name,datatype,alias=None,primary_key=None,
            tblinfo=None,weight=None,exp=None,func=None):
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
                
        if weight is None:
            weight = self._start_weight(parent)
        
        dbid,tblname = tblinfo['parent_db'],tblinfo['name']
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
            'parent_db':dbid,
            'weight':weight,
            'name':name,
            'alias':alias,
            'datatype':datatype,
            'owner':tblowner,
            'objid':colid,
            'dobj':func
        }
        
        
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
        
        if exp is not None:
            try:
                fname = exp['fname']
                args = exp['args']
            except TypeError:
                fname = exp[0]
                args = exp[1:]
            p = self.api.get_byid(parent)
            if fname in datatypes.valid:
                s,params = getattr(datatypes,fname).sql_cast(exp)
            else:
                raise errors.InvalidFunction
            stmt = syntax.update_as(p['parent_objid'],p.objid,colid,s)
            controllers['ddl'].execute(stmt,params)
        
        del(regVals['qtn'])
        Entity.create(self,regVals)
        
        controllers['ddl'].conn.commit()
        
        self.objid = colid
        
        return self
        
    def modify(self,params):
        """Change the type of a column."""
        if self['owner'] != self.session['user']:
            raise errors.NotAuthorized
        
        if 'datatype' in params:
            newtype = params['datatype']
            if newtype.startswith('datatype:'):
                newtype = newtype.replace('datatype:','')
            if newtype not in datatypes.valid:
                raise TypeError("Invalid type: " + newtype)
            typesql = getattr(datatypes,newtype).sql_create()
            colinfo = self.row_dict
            tblinfo = self.api.get_byid(colinfo['parent_objid'])
            
            if 'exp' not in params:
                mod_stmt = syntax.alter_column_type(
                    tblinfo['parent_objid'],
                    tblinfo['objid'],
                    colinfo['objid'],
                    typesql,
                    newtype
                )
                u_params = None
            else:
                args = {
                    'fname':newtype,
                    'args':[colinfo['objid'],params['exp']]
                }
                u_stmt, u_params = getattr(datatypes,newtype).sql_cast(args)
                # Need to test the validation for `newtype`
                mod_stmt = syntax.alter_column_type(
                    tblinfo['parent_objid'],
                    tblinfo['objid'],
                    colinfo['objid'],
                    typesql,
                    newtype,
                    u_stmt
                )
            
            controllers['ddl'].execute(mod_stmt,u_params)
            
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



