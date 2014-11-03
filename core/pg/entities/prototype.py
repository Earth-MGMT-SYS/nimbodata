"""Module implements the PostgreSQL Entity base class."""
# Copyright (C) 2014  Bradley Alan Smith

from uuid import uuid4 as uuid

import psycopg2

import common.errors as errors
import common.entities.prototype as base_ent
from .. import syntax

from . import *

class ReadOnlyDict(dict):
    """This is a local cache for the Entity info."""
    
    def __setitem__(self,key,value):
        raise TypeError("This here dict is read-only, pardner")
    
class Entity(base_ent.Entity):
    """Base class for an entity in a PostgreSQL database (in PG terms)."""
    schema = '_adm-registries'
    ent_reg = '_adm-entityregistry'
    ent_info = '_adm-entityinfo'
        
    def _by_name(self,name):
        """Assigns `self.objid` by a registry query for the name."""
        where = [
            ('name','=',name),
            ('entitytype','=',type(self).__name__)
        ]
        
        if type(self).__name__ != 'Database':
            try:
                where += [('parent_objid','=',str(self.parent))]
            except (TypeError,AttributeError):
                raise errors.RelationDoesNotExist
        
        stmt, params = syntax.select(
            self.schema,
            self.ent_info,
            where = where
        )
        
        try:
            return controllers['drc']._get_scalar('objid',stmt,params)
        except (IndexError,TypeError):
            raise errors.RelationDoesNotExist
    
    @property
    def info(self):
        try:
            if self._info:
                return self._info
        except AttributeError:
            pass
        
        objid = str(self.objid)
        
        stmt, params = syntax.select(self.schema,
                                     self.ent_info,
                                     where = ('objid','=',objid))
        
        try:
            retVal = dict(controllers['drc']._get_first(stmt, params))
        except TypeError:
            raise errors.RelationDoesNotExist
        
        try:
            if retVal['entitytype'] in ['View','Table']:
                try:
                    retVal['cols'] = [x.row_dict for x in self.columns()]
                except AttributeError:
                    retVal['cols'] = self.columns()
        except errors.RelationDoesNotExist: # Likely during the creation stage
            pass
        
        self._info = ReadOnlyDict(retVal)
        return self._info
    
    def select(self):
        """Get all children of this entity."""
        cols = self.attr_cols
        coltype = lambda x: x if x == 'dbid' else 'text'
        header = [{'name':x,'datatype': coltype(x),'weight':i}
                  for i,x in enumerate(cols)]
        
        where=[('parent','=',self['objid'])]
        
        stmt, params = syntax.select(
            self.schema,
            self.ent_info,
            where=where,
            order_by=('weight',)
        )
        
        infos = list(controllers['drc'].execute(stmt,params))
        retVal = []
        
        for i in infos:
            retVal.append(ent_map[i['entitytype']](objid=i['objid']))
            
        return retVal
    
    def tree(self):
        """Get all children of this entity."""
        if self.objid is None:
            where = [('owner','=',self.session['user'])]
        else:
            where = [('parent_objid','=',self.objid)]
        where += [
            ('entitytype', '!=', 'Constraint'),
            ('entitytype', '!=', 'Column'),
            ('name', '!=', 'temp')
        ]
        cols = self.attr_cols
        coltype = lambda x: x if x == 'dbid' else 'text'
        header = [{'name':x,'datatype': coltype(x),'weight':i}
                  for i,x in enumerate(cols)]
        
        stmt, params = syntax.select(
            self.schema,
            self.ent_info,
            where=where
        )
        
        stmt += """
            ORDER BY
            CASE
                WHEN entitytype='Database' THEN 1
                WHEN entitytype='Table' THEN 2
                WHEN entitytype='View' THEN 3
                WHEN entitytype='Column' THEN 4
                WHEN entitytype='Constraint' THEN 5
            END
        """
        
        infos = list(controllers['drc'].execute(stmt,params))
        retVal = []
        
        for i in infos:
            retVal.append(dict(i))
        
        if self.objid is not None:
            retVal = [self.info] + retVal
                
        return retVal
    
    def listing(self,child_type=None):
        """Get all peers or children of the entity.
        
        Called directly, it provides a list of same-type siblings.
        
        The method also serves a `__getattr__` for the lowercase plural of any
        entity type (i.e. `Database().tables()` or `Table().columns()`).  When
        called via `__getattr__`, it will be called with the `child_type` 
        converted from the `attr` argument.
        
        """
        cols = self.attr_cols
        coltype = lambda x: x if x == 'dbid' else 'text'
        header = [{'name':x,'datatype': coltype(x),'weight':i}
                  for i,x in enumerate(cols)]
        
        if child_type is None:
            where=[('entitytype','=',type(self).__name__)]
            if self.objid is not None:
                where+=[('parent_objid','=',str(self['parent']))]
        else:
            where=[('entitytype','=',child_type)]
            if self.objid is not None:
                where+=[('parent_objid','=',str(self.objid))]
                
        if type(self).__name__ == 'Column':
            where += [('objid','!=','_adm-rowid')]
        
        stmt, params = syntax.select(
            self.schema,
            self.ent_info,
            where=where,
            order_by=('weight',)
        )
        
        infos = list(controllers['drc'].execute(stmt,params))
        retVal = []
        
        for i in infos:
            retVal.append(self.api.get_entity(i['entitytype'])(objid=i['objid']))
            
        return retVal
    
    def create(self,vals,temporary=False):
        """ Register an entity in the metadata registry.
        
        Default create method for an entity - only used in conjunction with
        an actual implementation of an Entity - because this only registers
        the entity in the registry - it does not execute the entity SQL
        itself.
        
        """
        self.parent = vals['parent_objid']
        name = self._by_name(vals['name'])
        if name is not None and temporary:
            pass
        elif name is not None:
            print vals['name']
            raise errors.RelationExists
        vals['entitytype'] = type(self).__name__
        if isinstance(vals['parent_objid'],Entity):
            vals['parent_objid'] = str(vals['parent_objid'].objid)
        if isinstance(vals['parent_db'],Entity):
            vals['parent_db'] = str(vals['parent_db'].objid)
        if vals['entitytype'] != 'Database':
            parent = self.api.get_byid(vals['parent_objid'])
            if parent['owner'] != self.session['user']:
                raise errors.NotAuthorized
        cols = sorted(vals.keys())
        registry = self.ent_reg
        
        stmt = syntax.insert(self.schema,registry,colnames=cols)
        try:
            controllers['ddl'].execute(stmt,vals)
            controllers['ddl'].conn.commit()
        except psycopg2.IntegrityError as e:
            if e.pgcode == '23502':
                # Integrity Error null value in column ...
                raise ValueRequired
            elif e.pgcode == '23505':
                raise RelationExists
            else:
                print '\n',e.pgcode
                print e.pgerror,'\n'
                raise e
    
    def _registry_insert(self,vals,registry=None):
        """Prepares and executes an insert into a registry."""
        cols = sorted(k for k in vals.keys() if k != 'methods')
        registry = self.ent_reg if registry is None else registry
        stmt = syntax.insert(self.schema,registry,colnames=cols)
        try:
            controllers['ddl'].execute(stmt,vals)
        except psycopg2.IntegrityError as e:
            if e.pgcode == '23502':
                # Integrity Error null value in column ...
                raise ValueRequired
            elif e.pgcode == '23505':
                raise RelationExists
            else:
                print '\n',e.pgcode
                print e.pgerror,'\n'
                raise e
        controllers['ddl'].conn.commit()
    
    def modify(self,params):
        """Update the metadata params for the entity."""
        if any(x in params for x in
                ('objid','parent_objid','cols','methods','entitytype')):
            raise errors.BadData
        info = self.info
        if self.session['user'] != info['owner']:
            raise errors.NotAuthorized
        if 'dobj' in params:
            try:
                params['dobj'] = info['dobj'].update(params['dobj'])
            except AttributeError:
                pass
        info.update(params)
        self._registry_insert(info)
        return self.info
    
    def rename(self,newname):
        """Rename the entity.
        
        Should work for all implementations that use Entity.create()
        
        """
        info = self.row_dict
        if self.session['user'] != info['owner']:
            raise errors.NotAuthorized
        info['name'] = newname
        self._registry_insert(info)
        return self.objid
    
    def drop(self):
        """Drop the entity.
        
        Does not execute the actual SQL required to drop the object - just 
        drops the entity from the registry.
        
        """
        info = self.info
        if self.session['user'] != info['owner']:
            raise errors.NotAuthorized
        
        stmt = syntax.delete_row(
            self.schema,
            self.ent_reg,
            ('objid','=',str(self.objid))
        )
        
        controllers['ddl'].execute(stmt)
        
        stmt = syntax.delete_row(
            self.schema,
            self.ent_reg,
            ('parent_objid','=',str(self.objid))
        )
        
        controllers['ddl'].execute(stmt)
        controllers['ddl'].conn.commit()
        return True
