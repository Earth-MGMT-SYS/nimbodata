"""Module implements Nimbodata proxy entities for the REST client."""
# Copyright (C) 2014  Bradley Alan Smith

import json
import sys
import inspect

import shapely.geometry as shp
import jsonpickle

import common.results as results
import common.comparable as comparable
from common.errors import *


_this_module = sys.modules[__name__]

def fallback_json(obj):
    try:
        return obj.objid
    except AttributeError:
        return obj.data
    
def init_entity(objid):
    if objid.startswith('dbi-'):
        return Database(objid=objid)
    elif objid.startswith('tbl-'):
        return Table(objid=objid)
    elif objid.startswith('viw-'):
        return View(objid=objid)
    elif objid.startswith('col-'):
        return Column(objid=objid)
    return Entity(objid=objid)

class Entity(object):
    
    def __init__(self,name=None,objid=None):
        """ If caller gave objid, instantiate from objid, else call create """
        
        if objid is None:
            self.objid = self._isid(name)
        else:
            self.objid = objid
            return
        
        if self.objid is not None:
            return
            
        if name is not None:
            self.objid = json.loads(sesh.get(self._get_req_url(name)).text)['objid']
        
            
    def _isid(self,obj):
        """
        If a valid objid for the object type is given somewhere in the
        args, return it.  Otherwise, return False.
        
        Used to parse `__init__` input to determine if `objid` was provided
        either positional or kwargs.
        
        """
        if not isinstance(obj,basestring):
            try:
                return str(obj.objid)
            except AttributeError:
                return None
        else:
            try:
                if len(obj) == 36 and obj[3] == '-':
                    return obj
                else:
                    return None
            except IndexError:
                return None
            
    def __getattr__(self, attr):
        """Dynamic lookup for method calls"""
        if attr.startswith('_'):
            raise errors.InvalidMethod
        elif attr.startswith('create_'):
            ent = getattr(_this_module,attr.split('_')[1].capitalize())()
            ent.sesh = self.sesh
            def inner(*args,**kwargs):
                args = [self] + list(args)
                return ent.create(*args,**kwargs)
            return inner
        
        
        def ent_wrap(entity):
            def inner(*args,**kwargs):
                ent = entity(*args,**kwargs)
                ent.sesh = self.sesh
                return ent
            return inner
            
        def get_func_wrap():
            return self._ent_func(attr)
            
        try:
            return ent_wrap(getattr(_this_module,attr))
        except AttributeError:
            return ent_wrap(getattr(_this_module,attr.capitalize()))
        
        return get_func_wrap
        
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
        r = self.sesh.get(root_url+method_name+"/")
        raw = json.loads(r.text)
        if not isinstance(raw,list):
            return raw
        instantiated = []
        for x in raw:
            ent = init_entity(x)
            ent.sesh = self.sesh
            instantiated.append(ent)
        return instantiated
        
    def __getitem__(self,item):
        inf = json.loads(sesh.get(self._get_req_url(self.objid)).text)
        return inf[item]
    
    @property
    def info(self):
        retVal = json.loads(sesh.get(self._get_req_url(self.objid)).text)
        return retVal
        
    def listing(self):
        items = json.loads(sesh.get(self._get_req_url()).text)
        entities = [init_entity(objid=x) for x in items]
        for e in entities:
            e.sesh = self.sesh
        return entities
        
    def create(self,kwargs):
        payload = json.dumps(kwargs,default=fallback_json)
        r = self.sesh.post(self._get_req_url(),data = payload)
        self.objid = json.loads(r.text)
        return self
            
    def rename(self,newname):
        payload = json.dumps({'newname':newname})
        return json.loads(sesh.put(self._get_req_url(self.objid)+"rename/",payload).text)
        
    def modify(self,newtype):
        payload = json.dumps({'newtype':newtype})
        return json.loads(sesh.put(self._get_req_url(self.objid)+"modify/",payload).text)
        
    def drop(self):
        response = sesh.delete(self._get_req_url(self.objid))
        if response.status_code == 410:
            raise RelationDoesNotExist
        return json.loads(response.text)
            

class Database(Entity):
                
    def create(self,name):
        return Entity.create(self,{"name":name})
        
    def Table(self,*args,**kwargs):
        # self and dbid are typically the first two args, we're gonna take the 
        # positional args, convert them to kwargs and inject the correct dbid
        # and return the object called correctly.
        tbl_create_args = inspect.getargspec(Table.create)[0][2:]
        kwargs.update(dict(zip(tbl_create_args,args)))
        kwargs['parent'] = self.objid
        return Table(**kwargs)
        
    def tables(self):
        url = self._get_req_url(self.objid) + "tables/"
        r = sesh.get(url).text
        try:
            return [Table(x) for x in json.loads(r)]
        except ValueError as e:
            print r
            raise e
            
    def views(self):
        url = self._get_req_url(self.objid) + "views/"
        r = sesh.get(url).text
        try:
            return [View(x) for x in json.loads(r)]
        except ValueError as e:
            print r
            raise e

class View(Entity):
    
    def create(self,parent,name,select):
        return Entity.create(self,{
            'parent':parent,
            'name':name,
            "select":select
        })
        
    def _get_select_url(self):
        return "%(server)s/select/%(objid)s/" % {
            'server':server,
            'objid':self.objid
        }
    
    def select(self,cols=None,join=None,where=None,
            group_by=None,order_by=None,limit=None):
    
        req_url = server + "/select/%(viewid)s/" % { 'viewid' : self.objid }
    
        kwargs = {
            'viewid':self.objid,
            'cols':cols,
            'join':join,
            'where':where,
            'group_by':group_by,
            'order_by':order_by,
            'limit':limit
        }
                
        payload = json.dumps(kwargs,default = fallback_json)
        r = sesh.post(req_url, data = payload)
        
        try:
            data = json.loads(r.text)
        except ValueError:
            print r.text
            raise ValueError
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
            
    def columns(self):
        url = self._get_req_url(self.objid) + "columns/"
        r = sesh.get(url).text
        try:
            return [Column(x) for x in json.loads(r)]
        except ValueError as e:
            print r
            raise e
        

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
            'parent':parent,
            'name':name,
            "cols":cols
        })
        
    def insert(self,values):
        try:
            payload = json.dumps({'values':values})
        except TypeError:
            values = process_insert(values)
            payload = json.dumps({'values':values})
                    
        r = json.loads(self.sesh.post(self._get_req_url(self.objid),data = payload).text)
        if isinstance(r,basestring) and r.startswith('!ERROR!'):
            raise IntegrityError
        else:
            return r
        
    def add_columns(self,cols):
        payload = json.dumps({'cols':cols},default=fallback_json)
        return json.loads(self.sesh.post(self._get_req_url(self.objid)+"add_columns",data = payload).text)


class Tree(Table):
    
    def create(self,dbid,trname,trowner):
        return Entity.create(self,{
            'parent':dbid,
            'name':tblname
        })
        

class Column(Entity, comparable.Comparable):
    
    def create(self,tblid,colname,dtype,colalias=None,primary_key=None):
        return Entity.create(self,{
            'parent':tblid,
            'name':colname,
            'datatype':dtype,
            'alias':colalias
        })
        

class Constraint(Entity):
    
    def create(self,const):
        return Entity.create(self,{'const':const})
