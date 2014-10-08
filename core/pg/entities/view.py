"""Module implements the PostgreSQL view."""
# Copyright (C) 2014  Bradley Alan Smith

from pprint import pprint

from .. import syntax, select
from . import *
from common import tilecalc

import common.entities.view as base_view

_s = select.Select()

class View(base_view.View,Entity):
    """A view represents a query subject, such as a table or another view."""
    
    view_cols = '_adm-viewcolumns'
    view_col_info = '_adm-viewcolinfo'
    
    def create(self,parent_objid,name,select,temporary=False,materialized=True):
        """Create and register."""
        viewid = self._new_id()
        
        Entity.create(self,{
            'parent_objid':parent_objid,
            'name':name,
            'owner':self.session['user'],
            'objid':viewid
        },temporary)
        
        select['alias'] = False
        if 'cols' in select and select['cols'] is not None:
            select['cols'] = ['_adm-rowid'] + select['cols']
            select['viewcreate'] = True
            sel_stmt, sel_params, out_colinfo = _s._prepare_select(**select)
        else:
            sel_stmt, sel_params, out_colinfo = _s._prepare_select(**select)
            select['cols'] = ['_adm-rowid'] + [x['objid'] for x in out_colinfo]
            select['viewcreate'] = True
            sel_stmt, sel_params, out_colinfo = _s._prepare_select(**select)
        
        Entity.create(self.api.get_entity('Column')(),{
            'parent_objid':viewid,
            'weight':0,
            'name':'rowid',
            'datatype':'text',
            'entitytype':'Column',
            'owner':self.session['user'],
            'objid':"_adm-rowid",
            'alias':'Row ID',
        })
        
        for i,col in enumerate(out_colinfo):            
            try:
                regVals = {
                    'viewid':viewid,
                    'weight':i,
                    'colid':col['objid'],
                    'datatype':col['datatype']
                }
            except TypeError:
                regVals = {
                    'viewid':viewid,
                    'weight':i,
                    'colid':col[0]['objid'],
                    'datatype':col[0]['datatype']
                }
            
            if not isinstance(col,dict):
                col = col.row_dict
            if 'newcol' in col:
                col['parent_objid'] = viewid
                del(col['methods'])
                del(col['newcol'])
                Entity.create(self.api.get_entity('Column')(),col)
            self._registry_insert(regVals,self.view_cols)
            
        try:
            if not parent_objid.startswith('dbi'):
                parent_objid = self.api.get_byid(parent_objid)['parent_objid']
        except AttributeError:
            if not isinstance(parent_objid,self.api.get_entity('Database')):
                parent_objid = self.api.get_byid(parent_objid)['parent_objid']
        
        view_stmt = syntax.create_view(parent_objid,viewid,sel_stmt,
            materialized = materialized)
        
        #print view_stmt
                        
        controllers['ddl'].execute(view_stmt, sel_params)
        controllers['ddl'].conn.commit()
        
        if materialized is True:
            for col in self.columns():
                print 'Added index To: ', col['name']
                self.add_index(col)
            #self.add_index('_adm-rowid')
        
        self.objid = viewid
        return self
        
    def _new_indid(self):
        """Gets a new rowid for an inserted row."""
        return 'ind-'+str(uuid()).replace('-','')
    
    def add_index(self,col,unique=False):
        geocolnames = [x['name'] for x in self.geo_columns()]
        colinfo = self.api.get_entity('Column')(col).info
        index_type = 'GIST' if colinfo['name'] in geocolnames else None
        
        parent_objid = self.info['parent_objid']
        try:
            if not parent_objid.startswith('dbi'):
                parent_objid = self.api.get_byid(parent_objid)['parent_objid']
        except AttributeError:
            if not isinstance(parent_objid,self.api.get_entity('Database')):
                parent_objid = self.api.get_byid(parent_objid)['parent_objid']
        
        tblname = self.info['name']
        dbid = parent_objid
        tblid = self.info['objid']
        tblowner = self.info['owner']
        stmt = syntax.add_index(
            dbid,tblid,self._new_indid(),colinfo['objid'],unique,index_type
        )
        controllers['ddl'].execute(stmt)
        controllers['ddl'].conn.commit()
        return self.info
            
    def columns(self):
        """Get a list of columns in the relation."""
        viewid = str(self.objid)
        
        cols = self.attr_cols
                
        header = [{'name':x,'weight':i} for i,x in enumerate(cols)]

        stmt, params = syntax.select(
            self.schema,
            self.view_col_info,
            where = [('viewid','=',viewid),('name','!=','rowid')],
            order_by = ['weight']
        )
        
        return [dict(x) for x in controllers['drc'].execute(stmt,params)]
        
    def get_q_cols(self,select):
        """Get the columns resulting from a query without fetching rows."""
        select_viewid = str(select['objid'])
        select['schemaid'] = Entity(select_viewid)['parent']
        select['limit'] = 0
        try:
            select['tblid'] = select['objid']
            del(select['objid'])
        except KeyError:
            pass
        sel_stmt, sel_params = syntax.select(**select)
        with controllers['drc'].conn as conn:
            with conn.cursor() as cur:
                cur.execute(sel_stmt,sel_params)
                retVal = [
                    self.api.get_entity('Column')(objid=desc[0])
                        for desc in cur.description[2:]
                ]
        return retVal
    
    def select(self,*args,**kwargs):
        """Select from the relation, `self.objid` is provided to select."""
        # self and dbid are typically the first two args, we're gonna take the 
        # positional args, convert them to kwargs and inject the correct tblid
        # and return select.
        sel_func = select.Select().select
        select_args = inspect.getargspec(sel_func)[0][2:]
        kwargs.update(dict(zip(select_args,args)))
        kwargs['objid'] = self.objid
        return sel_func(**kwargs)
        
    def features(self,rowids,z=None):        
        geocols = self.geo_columns()
        tblinfo = Entity(objid=str(self.objid))
        geocolid = geocols[0]['objid']
        geocolname = geocols[0]['name']
        features = []
        
        dbid = tblinfo['parent_objid']
        tblid = tblinfo['objid']
        
        stmt = syntax.select_features_byrowid(
            dbid,
            tblid,
            geocolid,
            geocolname,
            rowids,
            z
        )
        
        r = controllers['dql'].execute(stmt)
        
        for row in r:
            features.append({
                'type':'Feature',
                'geometry':json.loads(row[1]),
                'properties':{
                    'rowid':row[0]
                }
            })
        
        return {
            'type':'FeatureCollection',
            'features':features
        }
        
    def tile_rowids(self,x,y,z):
        geocols = self.geo_columns()
        tblinfo = Entity(objid=str(self.objid))
        geocolid = geocols[0]['objid']
        geocolname = geocols[0]['name']
        features = []
        corners = tilecalc.tileBB(int(x),int(y),int(z))
        
        if tblinfo['parent_objid'].startswith('tbl'):
            tbl = self.api.get_entity('Table')(joininfo['parent_objid'])
            tblinfo['parent_objid'] = tbl['parent_objid']
        
        dbid = tblinfo['parent_objid']
        tblid = tblinfo['objid']
        
        stmt = syntax.select_geography_rowids(
            dbid,
            tblid,
            geocolid,
            corners,
            z
        )
                
        r = controllers['dql'].execute(stmt)
        
        return [x[0] for x in r]
    
    def tile(self,x,y,z):
        geocols = self.geo_columns()
        if len(geocols) == 0:
            return
        tblinfo = self.api.get_byid(self.objid)
        geocolid = geocols[0]['objid']
        geocolname = geocols[0]['name']
        geocoltype = geocols[0]['datatype']
        features = []
        if z > 2:
            corners = tilecalc.tileBB(int(x),int(y),int(z))
        else:
            corners = None
        
        if not tblinfo['parent_objid'].startswith('dbi'):
            tbl = api.get_byid(tblinfo['parent_objid'])
            try:
                tblinfo['parent_objid'] = tbl['parent_objid']
            except TypeError:
                tblinfo = tblinfo.row_dict
                tblinfo['parent_objid'] = tbl['parent_objid']
        
        dbid = tblinfo['parent_objid']
        tblid = tblinfo['objid']
        
        if geocoltype == 'Polygon' or geocoltype == 'MultiPolygon':
            stmt = syntax.select_geography_poly(
                dbid,
                tblid,
                geocolid,
                geocolname,
                corners,
                z=z
            )
        else:
            stmt = syntax.select_geography(
                dbid,
                tblid,
                geocolid,
                geocolname,
                corners,
                z=z
            )

        r = controllers['dql'].execute(stmt)
        
        for row in r:
            features.append({
                'type':'Feature',
                'geometry':json.loads(row[1]),
                'properties':{
                    'rowid':row[0]
                }
            })
        
        return {
            'type':'FeatureCollection',
            'features':features
        }
