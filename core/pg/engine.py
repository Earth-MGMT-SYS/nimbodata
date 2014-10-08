"""Module encapsulates PG access at a certain permission level."""
# Copyright (C) 2014  Bradley Alan Smith

import psycopg2
import psycopg2.extras

import common.errors as errors
import datatypes

_mode = 'debug'        


class Engine(object):
    """Engine for PostgreSQL database."""

    def __init__(self,user=None,drc=None):
        """Connect to the database and store the registries."""
        if user is None:
            self.user = 'cloud_admin'
        else:
            self.user = user
        
        self.conn = psycopg2.connect(self.conn_string)
        self.schema = '_adm-registries'
        self.ent_reg = '_adm-entityregistry'
        self.ent_info = '_adm-entityinfo'
        self.usr_reg = '_adm-userregistry'
        self.view_col_info = '_adm-viewcolinfo'
        self.mog_cur = self.conn.cursor()
        
    @property
    def conn_string(self):
        return 'dbname=cloud_admin user=%(user)s' % {
            'user':self.user
        }

    def close(self):
        self.conn.close()

    def execute(self,stmt,params=None):
        """Execute the statement in a transaction, parameters optional."""
        with self.conn as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                args = (stmt,) if params is None else (stmt,params)
                #print self.mogrify(*args)
                try:
                    cur.execute(*args)
                except psycopg2.IntegrityError:
                    raise errors.IntegrityError
                except psycopg2.DataError:
                    raise errors.DataError
                except psycopg2.ProgrammingError:
                    #print self.mogrify(*args)
                    raise
                try:
                    return list(cur)
                except psycopg2.ProgrammingError:
                    return None

    def execute_many(self,stmts,return_cursors=False):
        """Execute multiple statements within a transaction.
        
        Optionally return the cursors resulting from each.
        
        """
        if return_cursors is True:
            return [self.execute(x) for x in stmts]
        else:
            for x in stmts:
                self.execute(x)
    
    def mogrify(self,stmt,params=None):
        """Combines statement and params to string for human use."""
        cur = self.conn.cursor()
        return cur.mogrify(stmt,params)
    
    def _get_first(self,stmt,params=None):
        """Get the first row from a result."""
        try:
            r = self.execute(stmt,params)
        except psycopg2.ProgrammingError as e:
            print stmt
            raise e
        try:
            return next(x for x in r)
        except StopIteration:
            return None

    def _get_scalar(self,col,stmt,params=None):
        """Get the first value from the first row of a result."""
        try:
            return self._get_first(stmt,params)[col]
        except TypeError:
            return None
