"""Module implements Nimbodata proxy entities for the REST client."""
# Copyright (C) 2014  Bradley Alan Smith

import json
import sys
import inspect
import datetime

import shapely.geometry as shp
import jsonpickle

import common.results as results
import common.expressions as expressions
import common.errors as errors
import common.datatypes as datatypes

import common.entities.prototype as base_ent
import common.api


def fallback_json(obj):
    if isinstance(obj,datetime.datetime) or isinstance(obj,datetime.date) \
            or isinstance(obj,datetime.time):
        return obj.isoformat()
    try:
        return obj.objid
    except AttributeError:
        try:
            return obj.data
        except:
            try:
                return json.dumps(shp.mapping(obj))
            except AttributeError:
                print obj

def dump(obj):
    return json.dumps(obj,default=fallback_json)

    
_this_module = sys.modules[__name__]
    
def init_entity(objinfo):
    if objinfo['entitytype'] == 'Database':
        return Database(objid=objinfo['objid'])
    elif objinfo['entitytype'] == 'Table':
        return Table(objid=objinfo['objid'])
    elif objinfo['entitytype'] == 'View':
        return View(objid=objinfo['objid'])
    elif objinfo['entitytype'] == 'Column':
        return Column(objid=objinfo['objid'])
    return Entity(objid=objinfo['objid'])

class Entity(base_ent.Entity):
    
    _info = None
    
    def _by_name(self,name):
        try:
            return json.loads(sesh.get(self._get_req_url(name)).text)['objid']
        except ValueError:
            return json.loads(sesh.get(self._get_child_url(name)).text)['objid']
        
    def _get_child_url(self,child):
        
        templ = "%(server)s/%(class_name)s/%(objid)s/%(child_type)s/%(child_id)s/"
        return templ % {
            'server':server,
            'class_name':type(self.parent).__name__.lower() + 's',
            'objid':self.parent.objid,
            'child_type':self.__class__.__name__,
            'child_id':child
        }
        
    def _get_req_url(self,objid=None):
        classname = str(self.__class__.__name__).lower() + 's'
        if objid is None:
            templ = "%(server)s/%(class_name)s/"
        else:
            templ = "%(server)s/%(class_name)s/%(objid)s/"
        return templ % {
            'server':server,
            'class_name':classname,
            'objid':objid
        }
    
    def _ent_func(self,method_name):
        root_url = self._get_req_url(self.objid)
        r = sesh.get(root_url+method_name+"/")
        raw = json.loads(r.text)
        if not isinstance(raw,list):
            return raw
        instantiated = []
        for x in raw:
            ent = init_entity(x)
            ent.sesh = sesh
            instantiated.append(ent)
        return instantiated
        
    def __getitem__(self,item):
        inf = json.loads(sesh.get(self._get_req_url(self.objid)).text)
        return inf[item]
    
    @property
    def info(self):
        try:
            if self._info is None:
                self._info = json.loads(sesh.get(self._get_req_url(self.objid)).text)
            return self._info
        except AttributeError:
            self._info = json.loads(sesh.get(self._get_req_url(self.objid)).text)
            return self._info
        
    def listing(self,child_type=None):
        
        if child_type is None:
            items = json.loads(sesh.get(self._get_req_url()).text)
            entities = [init_entity(x) for x in items]
            for e in entities:
                e.sesh = sesh
            return entities
        else:
            url = self._get_req_url(self.objid) + ("%ss/" % child_type.lower())
            r = sesh.get(url).text
            try:
                return [api.get_entity(x['entitytype'])(x) for x in json.loads(r)]
            except ValueError as e:
                print r
                raise e
                
    def tree(self):
        url = self._get_req_url(self.objid) + ("tree/")
        return json.loads(sesh.get(url).text)
        
    def create(self,kwargs):
        payload = dump(kwargs)
        r = sesh.post(self._get_req_url(),data = payload)
        if r.status_code == 409:
            raise errors.RelationExists
        r_json = json.loads(r.text)
        self._info = r_json
        self.objid = self._info['objid']
        return self

            
    def rename(self,newname):
        payload = dump({'newname':newname})
        r = sesh.put(self._get_req_url(self.objid)+"rename/",payload)
        if r.status_code == 401:
            raise errors.NotAuthorized
        retVal = json.loads(r.text)
        self._info = None
        return retVal

        
    def modify(self,params):
        payload = dump({'params':params})
        try:
            self._info = None
            return json.loads(sesh.put(self._get_req_url(self.objid)+"modify/",payload).text)
        except ValueError:
            raise errors.DataError
        
    def drop(self):
        r = sesh.delete(self._get_req_url(self.objid))
        if r.status_code == 401:
            raise errors.NotAuthorized
        if r.status_code == 410:
            raise errors.RelationDoesNotExist
        return json.loads(r.text)
            

class Database(Entity):
                
    def create(self,name):
        return Entity.create(self,{"name":name})


class View(Entity):
    
    def create(self,parent,name,select,temporary=False,materialized=False):
        return Entity.create(self,{
            'parent_objid':parent.objid,
            'name':name,
            "select":select,
            'temporary':temporary,
            'materialized':materialized
        })
        
    def add_index(self,col,unique=False):
        payload = dump({'col':col,'unique':unique})
        return json.loads(sesh.post(self._get_req_url(self.objid)+"add_index/",data = payload).text)
        
    def _get_select_url(self):
        return "%(server)s/select/%(objid)s/" % {
            'server':server,
            'objid':self.objid
        }
    
    def select(self,cols=None,join=None,where=None,
            group_by=None,order_by=None,limit=None):
    
        req_url = server + "/select/%(viewid)s/" % { 'viewid' : self.objid }
    
        kwargs = {
            'objid':self.objid,
            'cols':cols,
            'join':join,
            'where':where,
            'group_by':group_by,
            'order_by':order_by,
            'limit':limit
        }
                
        payload = dump(kwargs)
        r = sesh.post(req_url, data = payload)
        
        try:
            data = json.loads(r.text)
        except ValueError:
            print r.text
            raise ValueError
            if r.status_code == 410:
                raise RelationDoesNotExist
        if isinstance(data,basestring) and data.startswith("!ERROR!"):
            raise RelationDoesNotExist            
        return results.Results(data['header'],data['rows'])
    
    def column(self,name):
        url = self._get_req_url(self.objid)+ ("column/%s/" % name )
        r = sesh.get(url).text
        try:
            return Column(json.loads(r))
        except ValueError as e:
            print r
            raise e
            
    def tile(self,x,y,z):
        url = self._get_req_url(self.objid) + 'tile/'
        url += ('/'.join(str(i) for i in (x,y,z)) + '/')
        return json.loads(sesh.get(url).text)
            
    def tile_rowids(self,x,y,z):
        url = self._get_req_url(self.objid) + 'tile_rowids/'
        url += ('/'.join(str(i) for i in (x,y,z)) + '/')
        return json.loads(sesh.get(url).text)
        
    def features(self,rowids,z=None):
        url = self._get_req_url(self.objid) + 'features/'
        payload = json.dumps({'rowids':rowids,'z':z})
        return json.loads(sesh.post(url,data=payload).text)
        

def process_insert(values):
    if hasattr(values,'__iter__'):
        try:
            return values.wkt
        except AttributeError:
            pass
        retVal = []
        for x in values:
            val = process_insert(x)
            retVal.append(val)
        return retVal
    else:
        try:
            return values.wkt
        except AttributeError:
            return jsonpickle.encode(values)

class Table(View):
    
    def create(self,parent,name,cols=[]):
        return Entity.create(self,{
            'parent_objid':parent.objid,
            'name':name,
            "cols":cols
        })
        
    def insert(self,values):
        try:
            payload = json.dumps({'values':values})
        except TypeError:
            values = process_insert(values)
            payload = json.dumps({'values':values})
                    
        r = json.loads(sesh.post(self._get_req_url(self.objid),data = payload).text)
        if isinstance(r,basestring) and r.startswith('!ERROR!'):
            raise errors.IntegrityError
        else:
            return r
        
    def add_columns(self,cols):
        payload = dump({'cols':cols})
        return json.loads(sesh.post(self._get_req_url(self.objid)+"add_columns/",data = payload).text)


class Column(Entity, expressions.Comparable):
    
    def create(self,tblid,colname,dtype,colalias=None,primary_key=None):
        return Entity.create(self,{
            'parent_objid':tblid,
            'name':colname,
            'datatype':dtype,
            'alias':colalias
        })
        
    def __getattr__(self,attr):
        func = getattr(getattr(datatypes,self.info['datatype']),attr)
        def outer(other):
            return func(self,other)
        return outer
                

class Constraint(Entity):
    
    def create(self,const):
        return Entity.create(self,{'const':const})

api = common.api.CloudAPI([Entity,Database,View,Table,Column,Constraint])

