
import json
from uuid import uuid4 as uuid
import sys

_this_module = sys.modules[__name__]

class Entity(object):
    
    objid_prefix = None
    attr_cols = (
        'name',
        'owner',
        'objid',
        'parent_objid',
        'entitytype',
        'datatype',
        'datadetail',
        'weight',
        'alias',
        'cols'
    )   
    
    def __init__(self,name=None,objid=None,info=None):
        """Instantiate the entity by name, object id or anonymously.        
        
        If caller gave objid, instantiate from objid.  Otherwise, try to
        instantiate by name from the function params.  Critical difference
        from the semantics of the REST API: instantiating an Entity by init
        params will fail if the object does not already exist - you must
        explicitly create the object either using a factory method or
        Entity().create().
        
        """
        self.objid = None
                
        if info is not None:
            self.objid = info['objid']
            return
        else:
            try:
                self.objid = name['objid']
                return
            except TypeError:
                pass
            
        if name is not None:
            self.objid = self._isid(name)
            if self.objid is None:
                self.objid = self._by_name(name)
            return
        
        if objid is not None:
            self.objid = self._isid(objid)
    
    def __str__(self):
        return self.objid
        
    def __len__(self):
        return len(self.children)
    
    def _by_name(self,name):
        raise NotImplementedError
        
    def _new_id(self):
        """ Creates a new UUID4 prefixed with the correct objid prefix """
        return self.objid_prefix+'-'+str(uuid()).replace('-','')
    
    def _isid(self,obj):
        """
        If a valid objid for the object type is given somewhere in the
        args, return it.  Otherwise, return False.
        
        Used to parse `__init__` input to determine if `objid` was provided
        either positional or kwargs.
        
        """
        try:
            return obj['objid']
        except (TypeError,KeyError):
            pass
        
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
        try:
            api
        except NameError:
            api = self.api
        
        if attr.startswith('_'):
            raise AttributeError
        elif attr.startswith('create_'):
            return api.create_child(attr.split('_')[1],self)
        
        elif attr.capitalize()[:-1] in api.ent_map:
            return lambda: self.listing(child_type=attr.capitalize()[:-1])
        
        try:
            ent = api.get_entity(attr)
            ent.parent = self
            return ent
        except KeyError:
            pass
        
        raise AttributeError(attr)
    
    def __getitem__(self,item):
        """Using an entity as a dict will access the registry metadata."""
        return self.info[item]
        
    @property
    def row_dict(self):
        return self.info
        
    @property
    def info(self):
        raise NotImplementedError
        
    def listing(self):
        raise NotImplementedError
    
    @property
    def children(self):
        raise NotImplementedError
        
    def create(self,kwargs):
        raise NotImplementedError
            
    def rename(self,newname):
        raise NotImplementedError
        
    def modify(self,newtype):
        raise NotImplementedError
        
    def drop(self):
        raise NotImplementedError
