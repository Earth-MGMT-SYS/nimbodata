"""Module implements the PostgreSQL schema entity (database in Nimbodata)."""
# Copyright (C) 2014  Bradley Alan Smith

from psycopg2 import ProgrammingError

import common.errors as errors
import common.entities.database as base_db

from .. import syntax

from . import *

class Database(base_db.Database,Entity):
    """PostgreSQL Schema or Nimbodata Database."""
    
    def create(self,name):
        """Create and register."""
        dbid = self._new_id()
        
        Entity.create(self,{
            'name':name,
            'owner':self.session['user'],
            'objid':dbid,
            'parent_objid':self.session['user']
        })
        
        stmt = syntax.create_db(dbid)
        controllers['ddl'].execute(stmt)
        # Grant usage to each of the key agents
        for user in ('dql_agent','dml_agent','ddl_agent'):
            controllers['ddl'].execute(syntax.grant_usage(dbid,user))
        # Grant default select on tables to `dql_agent`
        controllers['ddl'].execute(syntax.alter_default(dbid,'dql_agent'))
        controllers['ddl'].conn.commit()
        self.objid = dbid
        return self
    
    def drop(self):
        """Drop the database."""
        if self['owner'] != self.session['user']:
            raise errors.NotAuthorized
        
        stmt = syntax.drop_db(self.objid)
        try:
            controllers['ddl'].execute(stmt)
        except ProgrammingError:
            raise errors.RelationDoesNotExist
        
        for table in self.tables():
            for column in table.columns():
                column.drop()
            for view in table.views():
                for column in view.columns():
                    try:
                        column.drop()
                    except errors.RelationDoesNotExist:
                        pass
                view.drop()
        
        Entity.drop(self)
        
        return True
