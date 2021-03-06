"""Module implements PostgreSQL constraints."""
# Copyright (C) 2014  Bradley Alan Smith

try:
    import common.entities.constraint as base_constraint
except ImportError:
    import nimbodata.common.entities.constraint as base_constraint

from .. import syntax
from . import *

class Constraint(base_constraint.Constraint,Entity):
    """A PostgreSQL constraint as a Nimbodata Entity."""
    
    con_reg = '_adm-constregistry'
        
    def create(self, const):
        """Create the constraint and register it."""
        if const['tblid']:
            tblinfo = self.api.get_entity('Table')(objid=const['tblid'])
        
        cols = self.api.get_entity('Table')(objid=tblinfo['objid']).columns()
        
        conid = self._new_id()
        
        if 'cols' in const:
            cols = [x['objid'] for x in cols if x['name'] in const['cols']]
        else:
            cols = [x['objid'] for x in cols if x['name'] == const['col']]
        
        try:
            contype = const['contype']
        except KeyError:
            contype = None
            
        try:
            conname = const['conname']
        except KeyError:
            conname = const['contype']
        
        
        
        if const['contype'] == 'check':
            stmt = syntax.add_constraint_check(
                tblinfo['parent_objid'],
                tblinfo['objid'],
                conid,
                (cols[0],const['op'],const['compval'])
            )
            controllers['ddl'].execute(stmt,{'compval':const['compval']})
        
        elif const['contype'] == 'notnull':
            stmt = syntax.add_constraint_notnull(
                tblinfo['parent_objid'],
                tblinfo['objid'],
                cols[0]
            )
            controllers['ddl'].execute(stmt)
        
        elif const['contype'] == 'unique':
            stmt = syntax.add_constraint_unique(
                tblinfo['parent_objid'],
                tblinfo['objid'],
                conid,
                cols[0]
            )
            controllers['ddl'].execute(stmt)
            
        elif const['contype'] == 'primary':
            stmt = syntax.add_primarykey(
                tblinfo['parent_objid'],
                tblinfo['objid'],
                conid,
                cols
            )
            controllers['ddl'].execute(stmt)
        
        Entity.create(self,{
            'objid':conid,
            'cols':cols,
            'name':conname,
            'datatype':contype,
            'parent_objid':const['tblid'],
            'parent_db':const['tblid'],
            'owner':self.session['user']
        })
        
        controllers['ddl'].conn.commit()
        
        self.objid = conid
        return self
        
    def drop(self):
        """Drop the constraint from the table."""
        
        coninfo = self.info
        Entity.drop(self)
        
        tblinfo = self.api.get_entity('Table')(coninfo['parent_objid'])
        
        if coninfo['datatype'] != 'notnull':
            stmt = syntax.drop_constraint(
                tblinfo['parent_objid'],
                tblinfo['objid'],
                coninfo['objid']
            )
        else:
            stmt = syntax.drop_constraint_notnull(
                tblinfo['parent_objid'],
                tblinfo['objid'],
                coninfo['cols'][0]
            )
        
        controllers['ddl'].execute(stmt)
        
        return True
