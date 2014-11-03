"""Module implements the Python/REST client for Nimbodata"""
# Copyright (C) 2014  Bradley Alan Smith

import json
import sys
import inspect

import requests

import common.errors as errors
from common.errors import *
import common.results as results
import common.expressions

import entities


sesh = entities.sesh = requests.session()
api = entities.api

def connect(server,user):
    """Connect to the server as the user and return a cloud proxy."""
    sys.modules[__name__].server = server
    entities.server = server
    sesh.post(server+"/login/",json.dumps({'user':user,'pass':'asswort'}))
    api.session = {'user':user}
    return Cloud()

class Cloud(object):
    """Local proxy for Nimbodata via REST."""
        
    def __getattr__(self, attr):
        """Dynamic lookup for method calls"""
        return api.get_attr(attr)
        
    def get_byid(self,objid):
        """Instantiate the correct proxy object by ID."""
        objinfo = entities.Entity(objid=str(objid))
        objinfo.sesh = sesh
        entity = getattr(entities,objinfo['entitytype'])()
        entity.sesh = sesh
        entity.objid = objid
        return entity
        
    def get_byrowid(self,tblid,rowid,alias=False):
        req_url = server + "/get_byrowid/%s/%s/%s/" % (tblid.objid,rowid,alias)
        return json.loads(sesh.get(req_url).text)
        
    def get_array(self,objid=None,col=None,join=None,where=None,
            group_by=None,order_by=None,limit=None):
        
        req_url = server + "/get_array/%(objid)s/" % { 'objid' : objid.objid }
    
        kwargs = {
            'objid':objid,
            'col':col,
            'join':join,
            'where':where,
            'group_by':group_by,
            'order_by':order_by,
            'limit':limit
        }
                
        payload = json.dumps(kwargs,default = entities.fallback_json)
        r = sesh.post(req_url, data = payload)
        
        try:
            data = json.loads(r.text)
        except ValueError:
            print r.text
            raise ValueError
        if isinstance(data,basestring) and data.startswith("!ERROR!"):
            raise RelationDoesNotExist
        return data

    def select(self,objid=None,cols=None,join=None,where=None,
            group_by=None,order_by=None,limit=None,union=None):
    
        if objid is not None and not isinstance(objid,common.expressions.Union):
            req_url = server + "/select/%(objid)s/" % { 'objid' : objid.objid }
        
            kwargs = {
                'objid':objid,
                'cols':cols,
                'join':join,
                'where':where,
                'group_by':group_by,
                'order_by':order_by,
                'limit':limit
            }
                    
            payload = json.dumps(kwargs,default = entities.fallback_json)
        elif isinstance(objid,common.expressions.Union) or union is not None:
            if union is None:
                union = objid
            qa = union.fargs[0]
            req_url = server + "/select/%(objid)s/" % { 'objid' : qa['objid'] }
            
            payload = json.dumps(union,default = entities.fallback_json)
        
        r = sesh.post(req_url, data = payload)
        
        try:
            data = json.loads(r.text)
        except ValueError:
            if r.status_code == 410:
                raise RelationDoesNotExist
            else:
                print r.text
                raise ValueError
        if isinstance(data,basestring) and data.startswith("!ERROR!"):
            raise RelationDoesNotExist
        return results.Results(data['header'],data['rows'])
        
            
        
    def _cont_func(self,verb,cont_name,fname):
        def inner(*args,**kwargs):
            req_url = server+"/%(cont_name)s/%(fname)s" % {'cont_name':cont_name,'fname':fname}
            argspec = self.api['controllers'][cont_name][fname]['args']
            kwargs.update(dict(zip(argspec,args)))
                        
            if verb == 'get':
                for k,v in kwargs.items():
                    if isinstance(v,entities.Entity):
                        kwargs[k] = v.objid
                
                r = sesh.get(req_url, params = kwargs)
            elif verb == 'post':
                payload = json.dumps(kwargs,default = entities.fallback_json)
                
                r = sesh.post(req_url, data = payload)
            data = json.loads(r.text)
            try:
                return results.Results(data['header'],data['rows'])
            except:
                return data
        return inner
