
from functools import partial
import copy
import inspect
from pprint import pprint

from flask import request
from flask.ext import login

import errors
from datatypes.fallback_json import pretty_dump

#logfile = open('../../log/trace','wa')

actions = {
    'create':'POST',
    'insert':'POST',
    'update':'PUT',
    'select':'GET',
    'rename':'PUT',
    'modify':'PUT',
    'drop':'DELETE'
}

def get_current_user():
    user = login.current_user.get_id()
    try:
        user = user if user is not None else request.headers['From']
    except KeyError:
        raise errors.NotAuthorized
    if user is None:
        raise errors.NotAuthorized 
    return user

def get_class_from_method(meth):
    for cls in inspect.getmro(meth.im_class):
        if meth.__name__ in cls.__dict__:
            return cls.__name__
    return None

def wrap_api(fname,f,permissions):
    return f
    if f.__name__ == 'inner':
        return f
    def inner(*args,**kwargs):
        context = {
            'fname':fname,
            'f':f
        }
        
        self = context['self'] = args[0]
        cls = context['cls'] = get_class_from_method(f)
        
        problem = False
        
        argz = self.api.get_args(cls,fname)
        argz = dict(zip(argz, args[1:]))
        argz.update(kwargs)
        
        context['argz'] = argz
        
        try:
            retVal = f(*args,**kwargs)
        except TypeError as e:
            context['exception'] = e
            #logfile.write(pretty_dump(context))
            raise e
        
        context['return'] = retVal
        
        if problem:
            try:
                pass
                logfile.write(pretty_dump(context))
            except UnboundLocalError:
                pass
        
        return retVal
    return inner

class CloudAPI(object):
    """Encapsulates object heirarchy and argument specifications for an API."""
    
    def __init__(self,bases):
        """Walk the base API objects provided, build API."""
                
        self.api = {}
        self.bases = []
        self.ent_map = {}
        for base in bases:
            base_name = base.__name__
            self.ent_map[base_name] = base
            self.bases.append(base_name)
            self.api[base_name] = {}
            for member in inspect.getmembers(base,inspect.ismethod):
                if member[0].startswith('_'):
                    continue
                
                if member[0] in actions:
                    verb = actions[member[0]]
                else:
                    verb = 'GET'
                                    
                argspec = inspect.getargspec(member[1])
                self.api[base_name][member[0]] = {
                    'base':base_name,
                    'args':copy.deepcopy(argspec.args[1:]),
                    'verb':verb
                }
        
        self.api = copy.deepcopy(self.api)
        
        self.urls = self._build_rest(bases)
        
        for base in bases:
            for member in inspect.getmembers(base,inspect.ismethod):
                if member[0] in actions:
                    # Ain't no decorator when she's gone
                    wrapped = wrap_api(member[0],member[1],actions[member[0]])
                    setattr(base,member[0],wrapped)
    
    def _build_rest(self,bases):
        root = '/'
        urls = {}
                
        def get_url(path1,path2=None,path3=None):
            if path2 is not None and path3 is None:
                return root+'/'.join([path1,path2]) + '/'
            elif path2 is not None and path3 is not None:
                return root+'/'.join([path1,path2,path3]) + '/'
            else:
                return root+path1+'/'
    
        def get_function(basename,methodname,params):
            return self.get_function(basename,methodname)(**params)
            
        def get_method(basename,objid,methodname,params=None):
            if params is None:
                return self.get_method(basename,objid,methodname)()
            else:
                return self.get_method(basename,objid,methodname)(**params)
        
        def get_listing(basename,objid=None):
            if objid is None:
                return self.get_entity(basename)().listing()
            else:
                return self.get_byid(objid).listing()
                
        def get_info(basename,objid):
            return self.get_entity(basename)(objid)
        
        for apitem,base in zip(self.api.items(),bases):
            basename, baseparams = apitem
            
            gl = partial(get_listing,basename)
            gi = partial(get_info,basename)
            
            urls[('GET',get_url(basename))] = gl
            urls[('GET',get_url(basename.lower()+'s'))] = gl
            
            
            urls[('GET',get_url(basename,'<objid>'))] = gi
            urls[('GET',get_url(basename.lower()+'s','<objid>'))] = gi
            urls[('GET',get_url(basename,'<objid>','info'))] = gi
            urls[('GET',get_url(basename.lower()+'s','<objid>','info'))] = gi
            
            for methodname,method in baseparams.items():
                                
                gm = partial(get_method,basename=basename,methodname=methodname)
                gf = partial(get_function,basename,methodname)
                                
                if methodname == 'create':
                    urls[('POST',get_url(basename))] = gf
                    urls[('POST',get_url(basename.lower()+'s'))] = gf
                    continue
                elif methodname == 'insert':
                    urls[('POST',get_url(basename,'<objid>'))] = gm
                    urls[('POST',get_url(basename.lower()+'s','<objid>'))] = gm
                    urls[('POST',get_url(basename,'<objid>','insert'))] = gm
                    urls[('POST',get_url(basename.lower()+'s','<objid>','insert'))] = gm
                    continue
                elif methodname == 'drop':
                    urls[('DELETE',get_url(basename,'<objid>'))] = gm
                    urls[('DELETE',get_url(basename.lower()+'s','<objid>'))] = gm
                    urls[('DELETE',get_url(basename,'<objid>','delete'))] = gm
                    urls[('DELETE',get_url(basename.lower()+'s','<objid>','delete'))] = gm
                    continue
                elif methodname == 'rename':
                    urls[('PUT',get_url(basename,'<objid>'))] = gm
                    urls[('PUT',get_url(basename.lower()+'s','<objid>'))] = gm
                    urls[('PUT',get_url(basename,'<objid>','delete'))] = gm
                    urls[('PUT',get_url(basename.lower()+'s','<objid>','delete'))] = gm
                    continue
                                    
                urls[(method['verb'],get_url(basename,'<objid>',methodname))] = gm
                urls[(method['verb'],get_url(basename.lower()+'s','<objid>',methodname))] = gm
        
        return urls
    
    def get_args(self,base,method):
        """Get the argument names for the class and method."""
        return self.api[base][method]['args']
        
    def get_methods(self,base):
        """Get the available methods for an API class."""
        return self.api[base].keys()

    def _process_entity_name(self,entityname):
        if entityname.endswith('s'):
            entityname = entityname[:-1]
        return entityname.capitalize()

    def get_entity(self,entityname):
        entityname = self._process_entity_name(entityname)
        entity = self.ent_map[entityname]
        entity.api = self
        try:
            entity.session = {'user':get_current_user()}
        except AttributeError:
            entity.session = self.session
        return entity
        
    def get_function(self,entityname,functionname):
        return getattr(self.get_entity(entityname)(),functionname)
        
    def get_method(self,entityname,objid,methodname):
        return getattr(self.get_entity(entityname)(objid),methodname)
        
    def get_byid(self,objid):
        entityname = self.get_entity('Entity')(objid)['entitytype']
        return self.get_entity(entityname)(objid)
    
    def get_root_func(self,functionname):
        ent = self.get_entity('Select')()
        return getattr(ent,functionname)

    def get_attr(self,attr,parent=None):
        if attr.startswith('_'):
            raise InvalidMethod
        elif attr.startswith('create_'):
            return self.get_function(attr.split('_')[1],'create')
        if attr in self.bases:
            return self.get_entity(attr)
        try:
            return self.get_root_func(attr)
        except AttributeError:
            raise AttributeError(attr + " not in " + type(self).__name__)
            
    def create_child(self,entityname,parent):
        def inner(*args,**kwargs):
            ent = self.get_entity(entityname)()
            args = [parent] + list(args)
            return ent.create(*args,**kwargs)
        return inner
