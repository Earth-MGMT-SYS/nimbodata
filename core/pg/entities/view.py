"""Module implements the PostgreSQL view."""
# Copyright (C) 2014  Bradley Alan Smith

from .. import syntax, select
from . import *
from common import tilecalc

import common.entities.view as base_view

_s = select.Select()

class View(base_view.View,Entity):
    """A view represents a query subject, such as a table or another view."""
    
    view_cols = '_adm-viewcolumns'
    view_col_info = '_adm-viewcolinfo'
    
    def create(self,parent_objid,name,select):
        """Create and register."""
        viewid = self._new_id()
        
        Entity.create(self,{
            'parent_objid':parent_objid,
            'name':name,
            'owner':self.session['user'],
            'objid':viewid
        })
        
        select['alias'] = False
        if 'cols' in select:
            select['cols'] = ['_adm-rowid'] + select['cols']
            select['viewcreate'] = True
            sel_stmt, sel_params, out_colinfo = _s._prepare_select(**select)
        else:
            sel_stmt, sel_params, out_colinfo = _s._prepare_select(**select)
            select['cols'] = ['_adm-rowid'] + [x['name'] for x in out_colinfo]
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
            'alias':'Row ID'
        })
        
        for col in out_colinfo:
            regVals = {
                'viewid':viewid,
                'weight':col['weight'],
                'colid':col['objid']
            }
            
            self._registry_insert(regVals,self.view_cols)
        
        view_stmt = syntax.create_view(parent_objid,viewid,sel_stmt)
        
        controllers['ddl'].execute(view_stmt, sel_params)
        controllers['ddl'].conn.commit()
        
        self.objid = viewid
        return self
            
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
        
        infos = list(controllers['drc'].execute(stmt,params))
        retVal = []
        
        for i in infos:
            if i['name'] == '_adm-rowid':
                continue
            retVal.append(self.api.get_entity('Column')(objid=i['objid']))
            
        return retVal
        
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
        kwargs['viewid'] = self.objid
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
        tblinfo = Entity(str(self.objid))
        geocolid = geocols[0]['objid']
        geocolname = geocols[0]['name']
        features = []
        if z > 2:
            corners = tilecalc.tileBB(int(x),int(y),int(z))
        else:
            corners = None
        
        dbid = tblinfo['parent_objid']
        tblid = tblinfo['objid']
        
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
